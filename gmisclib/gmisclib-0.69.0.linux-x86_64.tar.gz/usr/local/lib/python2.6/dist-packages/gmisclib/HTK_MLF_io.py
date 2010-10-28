
"""This reads MLF (Master Label Files) for/from the HTK speech recognition
toolkit.
"""

import os
import glob
from gmisclib import die
from gmisclib.xwaves_errs import *

TIME_QUANTUM = 1e-7
# At 11025 Hz sampling rate.
# TIME_QUANTUM = 1e-7 * (11025.0/11000.0)

class ReferencedFileNotFound(Error):
	def __init__(self, *s):
		Error.__init__(self, *s)


def _findfile(f, postfix, verbose):
	"""Find a file.   Starting with a glob expression C{f}, strip off
	any .something suffix, then add on C{postfix}.
	If that glob evaluates to a file, return (d,f)
	where C{d} is the directory and C{f} is the filename (with postfix removed).
	Postfix would normally start with '.'.
	At the end, os.path.join(d, f) + postfix will name a file.
	"""
	if not f:
		return (None, None)
	d0, f0 = os.path.split(f)
	f0 = os.path.splitext(f0)[0]
	fx = os.path.join(d0, f0) + postfix
	if verbose:
		die.info("HTK_MLF_io._findfile: glob=%s" % fx)
	gl = glob.glob(fx)
	if verbose:
		die.info("HTK_MLF_io._findfile globs=%s" % ','.join(gl))
	if len(gl) == 0:
		raise ReferencedFileNotFound, fx
	assert len(gl) == 1, 'Too many alternatives for %s: %d' % (fx, len(gl))
	d1, f1 = os.path.split(gl[0])
	# assert f1.endswith(postfix)
	f1 = os.path.splitext(f1)[0]
	# f1 = f1[:-len(postfix)]
	if verbose:
		die.info("HTK_MLF_io._findfile d1=%s d1=%s" % (d1, f1))
	return (d1, f1)


def parse_label_line(s, tq):
	"""This parses a line from a MLF into a tuple.
	@param tq: time quantum (normally 1e-7 seconds)
	@type tq: L{float}
	@param s: line to be parsed
	@type s: C{str}
	@raise BadFileFormatError: when parsing is not possible.
	"""
	a = s.strip().split()
	la = len(a)
	if la == 1:
		if a[0] == '///':
			die.die("Sorry! cannot handle /// in MLF.")
		return a[0]	# name
	elif tq is None:
		raise ValueError, "File data needs time_quantum to be a number."
	elif la >= 3:
		tmp = (float(a[0])*tq, float(a[1])*tq, a[2])
		if la == 3:
			return tmp	# (start, end, name)
		tmp = list(tmp)
		a = a[3:]
		while a:
			tmp.append(float(a.pop(0)))	# Score or Auxscore
			if not a:
				break
			tmp.append(a.pop(0))	# Auxname
		return tuple(tmp)
	elif la == 2:
		return (float(a[0])*tq, a[1])	# (start, name)
	raise BadFileFormatError


def _get_symbols(fd, time_quantum):
	"""This reads part of a MLF, grabbing all the labels for one utterance."""
        sym = []
        while True:
                s = fd.readline()
                if s == '':
			break
                s = s.rstrip('\r\n')
                if s == '.':
                        break
		elif s != '':
                	sym.append( parse_label_line(s, time_quantum) )
        return sym


def readone(mlf_efn, postfix='.wav', datapath='.', strict=True,
		findfile=True, pathedit=None, time_quantum=TIME_QUANTUM,
		verbose=False):
	"""Read a single set of labels from a MLF file.
	You specify the labels as part of the extended filename, like this:
	name_of_MLF_file:name_of_labels'.    The function returns
	only a single value and raises an exception if the  extended
	filename is ambiguous.
	@type mlf_efn: string in the form "F:S"
	@rtype dict()
	@return: a dictionary that describes the labels as per
		L{readiter}.
	"""
	filename, subname = mlf_efn.split(':')
	candidate = None
	for x in readiter(filename, postfix=postfix, datapath=datapath,
			strict=strict, findfile=findfile,
			pathedit=pathedit, time_quantum=time_quantum,
			verbose=verbose):
		if subname in x['filespec']:
			if candidate is not None:
				raise ValueError, "Not unique: %s in %s" % (subname, filename)
			candidate = x
	return candidate


def readiter(mlf_fn, postfix='.wav', datapath='.', strict=True,
		findfile=True, pathedit=None,
		time_quantum=TIME_QUANTUM,
		verbose=False):
	"""Read a HTK Master Label (MLF) file.
	Datapath and pathedit are ways to deal with the
	situation where the MLF file has been moved, or (for other reasons)
	the filenames in the MLF file don't point to the actual data.
	@type strict: bool
	@param strict: If true, raise an exception if an audio file cannot be found.
	@type time_quantum: L{float}
	@param time_quantum: A factor to convert from the time information in the MLF
		to real units of time (like seconds).   Ideally, time_quantum=1e-7 seconds
		for MLF files, but that isn't exactly accurate for some sampling rates
		(like 11025 samples/sec) when the sampling interval is not an integral
		multiple of 100 nanoseconds.
	@rtype: list of dict (for L{read}) or an iterator producing dicts (for L{readiter}).
	@return: [ {'filespec':path, 'd': d, 'f': f, 'symbols': [...] }, ... ].  This is
		a list (or iterator) of dictionaries.    Each dictionary corresponds to
		one utterance, or one "label file" in the MLF.
		Attributes 'd' and 'f' are only present if findfile==True;
		C{os.path.join(x['d'], x['f'])} is a path to the corresponding audio.
		C{x['filespec']} is the path information in the MLF,
		C{x['i']} is an C{int} indexing which utterance this is within the MLF,
		and C{x['symbols']} is the label information for that utterance.
		It is a list of tuples produced by L{parse_label_line}.
	"""
	if pathedit is None:
		pathedit = os.path.join

	dmlf, fmlf = os.path.split(mlf_fn)

	try:
		fd = open(mlf_fn, 'r')
	except IOError, x:
		raise NoSuchFileError(*(x.args))
	l = fd.readline()
	assert l=='#!MLF!#\n', 'l=%s' % l
	i = 0
	while True:
		f = fd.readline()
		if f == '':
			break
		f = f.strip()
		if f == '':
			continue
		if f.startswith('"') and f.endswith('"'):
			f = f[1:-1]
		fspec = f
		rv = {'filespec': fspec, 'i': i}
		if findfile:
			if verbose:
				die.info("dmlf=%s; datapath=%s; f=%s" % (dmlf, datapath, f))
			try:
				d1, f1 = _findfile(pathedit(dmlf,datapath,f), postfix, verbose)
			except ReferencedFileNotFound, x:
				if strict:
					raise
				else:
					die.warn('No such file: %s from %s' % (x, fspec))
					_get_symbols(fd, None)
					continue
			else:
				rv['d'] = d1
				rv['f'] = f1
		rv['symbols'] = _get_symbols(fd, time_quantum)
		yield rv
		i += 1


def read(mlf_fn, **kw):
	return list( readiter(mlf_fn, **kw) )

read.__doc__ = readiter.__doc__


class writer(object):
	def __init__(self, mlf_fd, time_quantum=TIME_QUANTUM):
		assert time_quantum > 0.0
		self.fd = mlf_fd
		self.fd.writelines('#!MLF!#\n')
		self.nchunks = 0
		self.scale = 1.0/time_quantum

	def chunk(self, filespec, data):
		if self.nchunks > 0:
			self.fd.writelines('.\n')
		self.fd.writelines( [ '"%s"\n' % filespec,
					'\n'.join(data), '\n'
					]
				)
		self.nchunks += 1
		self.fd.flush()

	def threecol(self, filespec, tcdata):
		d = [ '%d %d %s' % (int(round(t0*self.scale)),
					int(round(te*self.scale)),
					lbl) 
			for (t0, te, lbl) in tcdata
			]
		self.chunk(filespec, d)

	def close(self):
		self.fd.writelines('\n')
		self.fd.flush()
		os.fsync(self.fd.fileno())
		self.fd = None	# Normally, this will close the file.

	def __del__(self):
		if self.fd is not None:
			self.close()


if __name__ == '__main__':
	import sys
	DATAPATH = None
	arglist = sys.argv[1:]
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '-datapath':
			DATAPATH = arglist.pop(0)
		else:
			die.die('Unrecognized argument: %s' % arg)
	for tmp in readiter(arglist[0], datapath=DATAPATH,
				findfile=(DATAPATH is not None)
				):
		print '[', tmp['filespec'], tmp.get('d', ''), tmp.get('f', ''), ']'
		for tmps in tmp['symbols']:
			if isinstance(tmps, tuple):
				print ' '.join([str(q) for q in tmps])
			else:
				print tmps
