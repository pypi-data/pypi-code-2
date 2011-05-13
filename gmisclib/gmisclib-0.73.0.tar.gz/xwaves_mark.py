"""Run as an independent program, this prints out the information
in a .out file, generated for/by ESPS Xmark.
If you give it a -a flag, it will print just a single attribute from the
header of the Xmark file.

For example:

xwaves_mark.py -a utterance

returns the top line, which is normally the transcribed utterance.
"""

import os
import sys
from gmisclib import die
import types
from gmisclib.xwaves_errs import *

DecrTol = 0.004999	# The maximum amount that time marks can decrease
			# before it is considered an error.


def _monotonize_tail(d):
	i = len(d)-1
	t = d[-1][0]
	sum = 0.0
	n = 0
	while i>=0 and isinstance(d[i], types.TupleType):
		if d[i][0] < t:
			break
		sum += d[i][0]
		n += 1
		i -= 1
	avg = sum/float(n)
	for j in range(i+1, len(d)):
		tt, label, ty = d[j]
		d[j] = (avg, label, ty)





PHONE = 1
WORD = 0

def write(fd, hdr, data, SortData=1):
	cs = hdr.get('_COMMENT', '').split('\n')
	for c in cs:
		fd.writelines('# %s\n' % c)
	for (k, v) in hdr.items():
		if k != '_COMMENT' and k != 'utterance':
			fd.writelines('%s %s\n' % (k, v))
	if hdr.has_key('utterance'):
		fd.writelines('** %s\n' % hdr['utterance'])
	else:
		fd.writelines('**\n')

	if SortData:
		tmp = data[:]
		tmp.sort()
		data = tmp

	last = None
	for (t, lbl, ty) in data:
		if t < last:
			raise DataOutOfOrderError((t, lbl, ty))
		if ty == WORD:
			fd.writelines('%s\n' % lbl)
		else:
			fd.writelines('\t%s\t%f\n' % (lbl, t))
		last = t



def read(filename):
	"""Read in .in files produced by ESPS xmark.
	Returns (header, data),
	where data is (time, word_or_phoneme, type),
	where type is 0 for words, 1 for phonemes.
	Times are guarenteed to be increasing inside the set of
	all words, and also inside the set of all phonemes.
	Word marks preceed the corresponding phoneme marks.
	"""

	hdr = {}
	if filename == '-':
		fd = sys.stdin
	else:
		try:
			fd = open(filename, "r")
		except IOError, x:
			raise NoSuchFileError(x)

	# First, we read the header:
	comments = []
	n = 0
	while True:
		l = fd.readline()
		n += 1
		if l == '':
			raise RuntimeError, 'Premature EOF / bad file format: %s:%d' % (filename, n)
		if l.startswith('#'):
			comments.append(l[1:].strip())
			continue
		if l.startswith('**'):
			hdr['utterance'] = l[2:].strip()
			# Header is terminated by a line starting '**'.
			break
		try:
			a, v = l.split(None, 1)
			# Header can contain attribute/value pairs.
		except ValueError:
			die.warn("Line %d:"%n + l)
			raise BadFileFormatError, '%s:%d' % (filename,n)
		hdr[a.strip()] = v.strip()

	# Now, we read in the data:
	d = []
	t_last = -1e30
	while True:
		l = fd.readline()
		n += 1
		if not l:		# EOF
			break
		ls = l.strip()
		if not ls:		# Ignore blank lines.
			continue
		if l[0].isspace():	# Segmentation information is indented.
			try:
				label, t = ls.split(None, 2)
			except ValueError:	# Only one thing on the line.
				die.warn("Incomplete file: File: %s, Line %d:(%s)"%(filename, n, ls))
				# This is not a fatal problem at the end, especially not
				# if the last label is silence.
				tmp = fd.readline()
				if tmp == '':	# OK.  Incomplete was last line.
					break
				raise BadFileFormatError, '%s:%d' % (filename, n)
			t = float(t)
			if t >= t_last:
				d.append((t, label, PHONE))	# Put a tuple on the list.
			elif t >= t_last - DecrTol:
				d.append((t, label, PHONE))	# Put a tuple on the list.
				_monotonize_tail(d)		# Force the times to be monotonic.
				die.warn("Time decreases slightly: %s:%d" % (filename, n))
			else:
				raise DataOutOfOrderError, 'time is decreasing: %s:%d' % (filename, n)
			t_last = t
		else:		# Words are not indented.
			d.append(ls)				# Put a string on the list.

	fd.flush()
	# os.fsync(fd.fileno())	# Commit to disk.
	fd = None	# This will close the file descriptor unless
			# (as in the case of sys.stdin) something else
			# is holding a reference.

	# Next, we need to add a null word to the beginning.  Recall that we report ending
	# times: without a null word, we only know when the first word ended, not when
	# it started.  It starts when the null word ends, of course.
	if len(d)>0 and isinstance(d[0], types.TupleType):
		d.insert(0, '')

	# Now, we go through on a second pass, and add timing information to the words.
	# We assume that the word comes first, then the phonemes into which it is segmented.
	defer = None		# Marking the position of the last word seen.
	last_t = None
	for i in range(len(d)):
		if isinstance(d[i], str):	# Word -- just the string.
			if defer is not None:
						# Go back, and fix up the previous word,
						# now that we have the ending time.
				d[defer] = (last_t, d[defer], WORD)
			defer = i
		else:		# Tuple: phoneme (segmentation)
			last_t = d[i][0]	# Remember the ending time of the phoneme.

	if defer is not None:
		d[defer] = (last_t, d[defer], WORD)

	hdr['_COMMENT'] = '\n'.join(comments)
	hdr['_NAME'] = filename
	hdr['_FILETYPE'] = 'xmark'
	hdr['NAXIS'] = 2
	hdr['NAXIS2'] = len(d)
	hdr['NAXIS1'] = 3
	hdr['TTYPE1'] = 'time'
	hdr['TUNIT1'] = 's'
	hdr['TTYPE2'] = 'label'
	hdr['TTYPE3'] = 'is_phoneme'

	return (hdr, d)


def mark_to_lab(data, ty):
	"""This function lets you take a mixed list
	of word and phone labels, such as provided
	by xwaves_mark.read(), and will select out
	one or the other type.
	Type is PHONE or WORD.
	"""
	return [(time, label) for (time, label, typ) in data if typ==ty ]



def combine_2labs(whdr, wd, phdr, pd, utterance, TOL=0.001):
	"""Combine two XLAB files into one XMARK file.
	It forces (within rounding errors) the words
	to enclose the phones."""

	import xwaves_lab

	hdr = phdr.copy()
	hdr.update(whdr)
	hdr['utterance'] = utterance

	dw = xwaves_lab.start_stop(wd, dropfirst=1)
	dp = xwaves_lab.start_stop(pd, dropfirst=1)

	o = []
	j = 0
	o.append( ( dp[0][0], '*', PHONE) )
	# print "PRE S - %f *" % dp[0][0]
	while j < len(dp) and dp[j][1] < dw[0][0]-TOL:
		# print "PRE S %d %f %f %s" % (j, dp[j][0], dp[j][1], dp[j][2])
		o.append( ( dp[j][1], dp[j][2], PHONE) )
		j += 1
	for (start, stop, w) in dw:
		# print "w %f %f %s" % (start, stop, w)
		w_appended = 0
		while j<len(dp) and dp[j][1]<stop+TOL and dp[j][0]<stop:
			if not w_appended and dp[j][2] != '*':
				# print "W %f %f %s" % (dp[j][0], stop, w)
				o.append( (dp[j][0], w, WORD) )
				w_appended = 1
			# print "IN S %d %f %f %s" % (j, dp[j][0], dp[j][1], dp[j][2])
			o.append( (dp[j][1], dp[j][2], PHONE) )
			j += 1
		if not w_appended:
			o.append( ( start, w, WORD) )
	while j < len(dp):
		# print "POST S %d %f %f %s" % (j, dp[j][0], dp[j][1], dp[j][2])
		o.append( (dp[j][1], dp[j][2], PHONE) )
		j += 1
	return (hdr, o)


__doc__ = read.__doc__

if __name__ == '__main__':
	arglist = sys.argv[1:]
	if arglist[0] == '-a':
		arglist.pop(0)
		key = arglist.pop(0)
		hdr, data = read(arglist.pop(0))
		print hdr[key]
	elif arglist[0] == '-tolab':
		import xwaves_lab
		arglist.pop(0)
		ty = int(arglist.pop(0))
		hdr, data = read(arglist.pop(0))
		xwaves_lab.write(sys.stdout, hdr, mark_to_lab(data, ty))
	elif arglist[0] == '-fromlab':
		import xwaves_lab
		arglist.pop(0)
		whdr, wd = xwaves_lab.read(arglist.pop(0))
		phdr, pd = xwaves_lab.read(arglist.pop(0))
		hdr, data = combine_2labs(whdr, wd, phdr, pd,
					whdr.get('utterance', phdr.get('utterance', '')),
					TOL=0.001)
		write(sys.stdout, hdr, data, SortData=1)
	else:
		print read(sys.argv[1])
