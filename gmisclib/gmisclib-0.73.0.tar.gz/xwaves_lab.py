"""Reads label files produced by ESPS xwaves.
Writes labels files that ESPS xwaves can read.
"""

import os
import sys
from gmisclib import die
from gmisclib.xwaves_errs import *


def read(filename, loose=0):
	"""read in .lab files produced by ESPS xlabel. returns (header, data).
	Data = [(time, label), ...].
	Note that leading or trailing spaces in the label are removed.
	"""
	HUGE = 1e30
	hdr = {}
	if filename == '-':
		fd = sys.stdin
	else:
		try:
			fd = open(filename, "r")
		except IOError, x:
			raise NoSuchFileError, x
	n = 0
	comments = []
	while True:
		l = fd.readline()
		n += 1
		if not l:
			raise BadFileFormatError, '%s:%d' % (filename, n)
		if l.startswith('#'):
			break
		if l.startswith('comment'):
			comments.append(l[len('comment'):].strip())
			continue
		try:
			a, v = l.split(None, 1)
		except ValueError:
			if loose:
				hdr[l.strip()] = ''
				loose -= 1
			else:
				die.warn( ("Line %d:" % n) + l.strip())
				raise BadFileFormatError, '%s:%d' % (filename, n)
		else:
			hdr[a.strip()] = v.strip()

	t_last = -HUGE
	d = []
	while True:
		l = fd.readline()
		if not l:
			break
		n += 1

		l = l.lstrip().rstrip('\r\n')
		if not l:
			continue	# Skip blank lines

		lsplit = l.split(None, 2)

		if len(lsplit)==2 and (l.endswith(' ') or l.endswith('\t')):
			t, junk = lsplit
			label = ''
		elif len(lsplit)==2 and loose > 0:
			loose -= 1
			t,junk = lsplit
			label = ''
			comments.append('Two columns: assuming third is empty: line %d: %s' % (n, l))
		elif len(lsplit) == 2:
			raise BadFileFormatError, 'Two columns: should be three: %s:%d' % (filename, n)
		else:
			t, junk, label = lsplit

		t = float(t)
		if t >= t_last:
			d.append((t, label))
		elif loose > 0:
			d.append((t, label))
			loose -= 1
		else:
			raise DataOutOfOrderError, '%s:%d' % (filename, n)
		t_last = t

	fd.flush()
	# os.fsync(fd.fileno())	# Commit to disk.
	fd = None	# This will close most files, except for sys.stdin
			# which has probably some other reference keeping
			# it open.

	hdr['_COMMENT'] = '\n'.join(comments)
	hdr['_NAME'] = filename
	hdr['_FILETYPE'] = 'xlabel'
	hdr['NAXIS'] = 2
	hdr['NAXIS2'] = len(d)
	hdr['NAXIS1'] = 2
	hdr['TTYPE1'] = 'time'
	hdr['TUNIT1'] = 's'
	hdr['TTYPE2'] = 'label'

	return (hdr, d)


def start_stop(d, dropfirst=False):
	"""Converts data in (end_time, label) format to (t_start, t_stop, label)"""
	o = []
	last = None
	for (time, label) in d:
		o.append( (last, time, label) )
		last = time
	if dropfirst and len(o)>0:
		o.pop(0)
	return o


def end_marks(d, beglabel, delta=0.001, interlabel=None):
	"""Converts data in a (start, stop, label) format to (end_time, label).
	It introduces extra labels if neccessary.
	A beginning label is required, to mark the start of the first segment."""
	if len(d) == 0:
		return []
	if interlabel is None:
		interlabel = beglabel
	start, stop, label = d[0]
	o = [ (start, beglabel), (stop, label) ]
	laststop = stop
	for (start, stop, label) in d[1:]:
		if start > laststop + delta:
			o.append( (start, interlabel) )
		o.append( (stop, label) )
		laststop = stop
	return o


def write(fd, header, data):
	"""Expects data in [(t, label), ...] form.
	"""
	h = {'font': '-misc-*-bold-*-*-*-15-*-*-*-*-*-*-*',
		'separator': ';',
		'nfields': ';'
		}
	h.update(header)
	d = list(data)
	d.sort()

	alist = h.items()
	alist.sort()
	for (a, v) in alist:
		if v != '':
			for tmp in str(v).split('\n'):
				fd.write('%s %s\n' % (a, tmp))
	fd.write('#\n')
	fd.flush()
	for (t, mark) in data:
		fd.write('%12.5f    -1  %s\n' % (t, str(mark).strip()))
	fd.flush()


if __name__ == '__main__':
	hdr, data = read(sys.argv[1])
	for (t, l) in data:
		print t, l
