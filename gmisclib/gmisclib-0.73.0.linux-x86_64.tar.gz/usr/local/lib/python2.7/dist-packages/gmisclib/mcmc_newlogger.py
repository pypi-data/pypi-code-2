
import os
import re
import cPickle

import numpy

import die
import avio
import gpkmisc as GM
import dictops
import load_mod

import mcmc_indexclass as IC

HUGE = 1e30

def ok(x):
	return -HUGE < x < HUGE

assert ok(1.0)
assert not ok(2*HUGE)

class WildNumber(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)


BadFormatError = avio.BadFormatError

class logger_base(object):
	def __init__(self, fd):
		self.writer = avio.writer(fd)


	def flush(self):
		self.writer.flush()


	def close(self):
		self.writer.close()


	def header(self, k, v):
		self.writer.header(k, v)
		self.writer.flush()


	def headers(self, hdict):
		kvl = list(hdict.items())
		kvl.sort()
		for (k, v) in kvl:
			self.header(k, v)


	def comment(self, comment):
		self.writer.comment(comment)
		self.writer.flush()


def _fmt(x):
	return IC.index_base._fmt(x)


class DBGlogger(logger_base):
	def __init__(self, fd):
		logger_base.__init__(self, fd)
		

	def add(self, uid, prms, map, logp, iter, extra=None, reason=None):
		"""Adds parameters to the log file.
		uid -- which subset of parameters,
		prms -- a vector of the actual numbers,
		map -- a dictionary mapping from parameter names to an index into the prms array.
		logp -- how good is the fit?  log(probability)
		iter -- an integer to keep track of the number of iterations
		"""

		if extra is not None:
			tmp = extra.copy()
		else:
			tmp = {}
		if reason is not None:
			tmp['why_logged'] = reason
		tmp.update({'uid': uid, 'iter': iter, 'logp': '%.1f' % logp})
		for (nm, i) in map.items():
			tmp[_fmt(nm)] = '%.2f' % prms[i]
		self.writer.datum(tmp)
		self.writer.flush()



class logger(logger_base):
	def __init__(self, fd, huge=1e30):
		"""Create a data log.
		@param fd: Where to log the results
		@type fd: file
		@param huge: sets a threshold for throwing L{WildNumber}.
			If the absolute value of any parameter gets bigger than huge,
			something is assumed to be wrong.
		@type huge: normally float, but could be numpy.ndarray
		"""
		logger_base.__init__(self, fd)
		self.nmmap = {}
		self.HUGE = huge


	def add(self, uid, prms, map, logp, iter, extra=None, reason=None):
		"""Adds a set of parameters to the log file.
		@param uid: which subset of parameters,
		@type uid: string
		@param prms: a vector of the actual numbers,
		@type prms: numpy.ndarray
		@param map: a dictionary mapping from parameter names to an index into the prms array.
		@type map: dict
		@param logp: how good is the fit?  log(probability)
		@type logp: float
		@param iter: which iteration is it?
		@type iter: int
		@param extra: any extra information desired.
		@type extra: None or a dictionary.
		"""
		deltanm = []
		for (nm, i) in map.items():
			k = (uid, i)
			if k not in self.nmmap or self.nmmap[k] != nm:
				self.nmmap[k] = nm
				deltanm.append( (i, nm) )
		if extra:
			tmp = extra.copy()
		else:
			tmp = {}
		if reason is not None:
			tmp['why_logged'] = reason
		tmp['uid'] = uid
		tmp['iter'] = iter
		wild = []
		if logp is None or ok(logp):
			tmp['logp'] = '%.2f' % logp
		else:
			wild.append("logp=%s" % str(logp))
		okprm = numpy.greater_equal(self.HUGE, prms) * numpy.greater_equal(prms, -self.HUGE)
		if not okprm.all():
			rmap = dictops.rev1to1(map)
			for (i,isok) in enumerate(okprm):
				if not isok:
					wild.append( 'p%d(%s)=%s' % (i, _fmt(rmap[i]), prms[i]) )
		tmp['prms'] = cPickle.dumps(prms, protocol=0)
		tmp['deltanm'] = cPickle.dumps(deltanm, protocol=0)
		self.writer.datum(tmp)
		self.writer.flush()
		if wild:
			raise WildNumber, '; '.join(wild)




class NoDataError(ValueError):
	"""There is not a complete set of data in the log file:
	data from the outer optimizer and at least one full set of inner optimizer
	results.
	"""
	def __init__(self, *s):
		ValueError.__init__(self, *s)


class logline(object):
	"""This holds the information from one line of a log file.
	For efficiency reasons, some of the data may be stored pickled,
	and should be accessed through C{prms()} or C{logp()}.
	"""

	__slots__ = ['uid', 'iter', '_logp', '_prms', 'names']

	def __init__(self, uid, iter, logp, prms, names):
		self.uid = uid
		self.iter = int(iter)
		self._logp = logp	# left as a string
		self._prms = prms	# This is a pickled value
		self.names = names

	def prms(self):
		tmp = cPickle.loads(self._prms)
		if len(tmp) != len(self.names):
			raise ValueError, "Problem unpickling logline: len=%d, should be %d" % (len(tmp), len(self.names))
		return tmp


	def logp(self):
		return float(self._logp)


def readiter(logfd, trigger=None):
	"""Reads in one line at a time from a log file.
	This is an iterator.   At every non-comment line, it yields an output.
	@param logfd: a L{file} descriptor for a log file produced by this module.
	@param trigger: this is None or a regular expression that specifies when to start paying
		attention to the data.  If C{trigger} is not None, body
		lines before C{trigger} matches are ignored.   Note that C{trigger}
		is matched to a line with trailing whitespace stripped away.
	@return: (Yields) C{(hdr, x)} where C{hdr} is a dictionary of the header information current
		at that point in the file and C{x} is a L{logline} class containing the current line's
		data.
	@except BadFormatError: ???
	@except KeyError: ???
	"""
	if trigger is not None:
		die.info('# Trigger="%s"' % trigger)
		trigger = re.compile("^#\s*" + trigger)
	hdr = {}
	nmmap = {}
	lineno = 0
	try:
		for line in logfd:
			lineno += 1
			if not line.endswith('\n'):
				break	# Incomplete last line of a file.
			line = line.rstrip()
			if line == '':
				continue
			if trigger is not None:
				if trigger.match(line):
					die.info("Trigger match")
					trigger = None
			if line.startswith('#'):
				if '=' in line:
					k, v = line[1:].split('=', 1)
					hdr[k.strip()] =  avio.back(v.strip())
				continue
			a = avio.parse(line)
			uid = a['uid']
			deltanm = cPickle.loads(a['deltanm'])

			# We do *NOT* unpickle a['prms'] here because the odds are very high
			# that no one will care about this particular set of parameters.
			# Unpickling is done, as needed, in the logline class.
			# prms = cPickle.loads(a['prms'])

			try:
				names = nmmap[uid]
			except KeyError:
				names = []
				nmmap[uid] = names
			if len(deltanm) > 0:
				olen = len(names)
				lmax = olen + len(deltanm)
				for (i, nm) in deltanm:
					if not ( 0 <= i < lmax ):
						raise BadFormatError, "Bad index for deltanm: old=%d i=%d len(names)=%d" % (olen, i, len(names))
					elif i < len(names):
						if names[i] is None:
							names[i] = nm
						elif names[i] != nm:
							raise BadFormatError, "Inconsistent names in slot %d: %s and %s" % (i, names[i], nm)
					else:
						names.extend([None]*(1+i-len(names)))
						names[i] = nm
				if None in names[olen:]:
					raise BadFormatError, "A name is none: %s" % names
				nmmap[uid] = names
			if trigger is None:
				yield (hdr, logline(uid, a['iter'], a['logp'], a['prms'],
							names)
					)
	except KeyError, x:
		raise BadFormatError, "Missing key: %s on line %d of %s" % (x, lineno, getattr(logfd, 'name', "?"))
	except BadFormatError, x:
		raise BadFormatError, "file %s line %d: %s" % (getattr(logfd, 'name', '?'), lineno, str(x))
	if trigger is not None:
		die.warn('Trigger set but never fired: %s' % getattr(logfd, 'name', '???'))



def read_raw(logfd):
	"""Read log information in raw line-by-line form."""
	data = []
	allhdrs = None
	for (hdr, datum) in readiter(logfd):
		data.append(datum)
		allhdrs = hdr
	return (allhdrs, data)



def _find_longest_suboptimizer(clidx):
	n = 0
	for (k, v) in clidx.items():
		lp = len(v.prms())
		if lp > n:
			n = lp
	return n


def _read_currentlist(fname, trigger):
	"""Starting from a file name, read in a log file.
	@param fname: name of a (possibly compressed) log file.
	@type fname: str
	@param trigger: where to start in the log file.  See L{readiter}.
	@rtype: C{(list(dict(str:X)), dict(str:str))} where C{X} is a
		L{logline} class containing the data from one line of the log file.
	@return: a list of data groups and header information.
		A data group is a dictionary of information, all from the same iteration.
		For simple optimizations, there is one item in a data group,
		conventionally under the key "UID".
	"""
	current = {}
	currentlist = []
	lastiter = -1
	lasthdr = None
	n_in_current = 0
	for (hdr, d) in readiter(GM.open_compressed(fname), trigger=trigger):
		# print '_read_currentlist: d=', str(d)[:50], "..."
		if d.iter!=lastiter and current:
			if lastiter >= 0:
				currentlist.append( current )
				current = {}
			lastiter = d.iter
		current[d.uid] = d
		n_in_current = max(n_in_current, len(current))
		lasthdr = hdr
	if n_in_current>0 and len(current) == n_in_current:
		currentlist.append(current)
	return (currentlist, lasthdr)



def read_log(fname, which):
	"""Read in a log file, returning information that you can use to
	restart the optimizer.   The log file must be produced
	by L{logger.add}().

	@param fname: the filename to read.
	@type fname: str
	@param which: a string that tells which log entry to grab.
		- "last": the final logged entry;
		- "index%d" (i.e. "index" followed directly by an integer):
			the %dth log entry (negative numbers count backwards from the end),
			so "index-1" is the final logged entry and "index0" is the first;
		- "frac%g" (i.e. "frac" followed by a float):
			picks a log entry as a fraction of the length of the log.
			"frac0" is the first, and "frac1" is the final entry.
		- "best": picks the iteration with the most positive logP value.
	@type which: str
	@return: (hdr, stepperstate, vlists, logps), where
		- hdr is all the header information from the log file
			(e.g. metadata).
		- stepperstate is a dictionary of L{IC.index} instances, one
			per UID and L{newstem2.position.OuterUID}.
			It will evoke a True when passed to
			L{newstem2.position.is_statedict}().
			Basically, this is a single moment of the stepper's state.
		- vlists is a dictionary (again, one per UID plus...) whose
			values are lists of position vectors that were recently
			encountered.   This is helpful for the optimizer to
			figure out plausible step sizes.
			Basically, this is many moments of state information near C{idx}.
		- logps is a dictionary (again...) whose values are recently
			obtained values for logP for that UID.   This is mostly
			useful for display and debugging purposes.
	@except NoDataError: ???
	"""
	def sumlogp(x):
		s = 0.0
		for v in x.values():
			s += v.logp()
		return s

	currentlist, lasthdr = _read_currentlist(fname, None)
	# currentlist is list(dict(str:X))
	if len(currentlist) == 0:
		raise NoDataError, fname

	if which == 'last':
		idx = len(currentlist)-1
	elif which == 'best':
		# Is this the appropriate definition of best?
		idx = 0
		slp = sumlogp(currentlist[idx])
		for (i,current) in enumerate(currentlist):
			tmp = sumlogp(current)
			if tmp > slp:
				idx = i
	elif which.startswith('frac'):
		frac = float(GM.dropfront('frac', which))
		if not ( 0 <= frac <= 1.0):
			raise ValueError, "Requires 0 <= (frac=%g) <= 1.0" % frac
		idx = int((len(currentlist))*frac)
	elif which.startswith('index'):
		idx = int(GM.dropfront('index', which))
		if not ( abs(idx) <= len(currentlist)):
			raise ValueError, "Requires abs(idx=%d) <= len(log_items)=%d" % (idx, len(currentlist))
		if idx < 0:
			idx = len(currentlist) + idx
	else:
		raise ValueError, "Bad choice of which=%s" % which

	n = _find_longest_suboptimizer(currentlist[idx]) + 1

	logps = {}
	vlists = {}
	stepperstate = {}
	lc = len(currentlist)
	assert lc > 0
	for (k, v) in currentlist[idx].items():
		# k is the name of a sub-optimizer
		# v is information about that sub-optimizer's idx^th iteration.
		lo = int(round(idx*float(max(0,lc-n))/float(lc)))
		assert 0 <= lo < lc
		high = min(2*n + lo, lc)
		assert lo < high <= lc, "lc=%d, lo=%d, idx=%d, n=%d" % (lc, lo, idx, n)
		keymap = dict([(key, i) for (i, key) in enumerate(v.names)])
		stepperstate[k] = IC.index(keymap, p=v.prms(), name=str(k))
		vlists[k] = [c[k].prms() for c in currentlist[lo:high]]
		logps[k] = v.logp()
	return (lasthdr, stepperstate, vlists, logps)


def read_multilog(fname, Nsamp=10, tail=0.5):
	"""Read in a log file, producing a sample of stepperstate information.
	@param tail: Where to start in the file?
		C{tail=0} means that you start at the trigger or beginning.
		C{tail=1-epsilon} means you take just the last tiny bit of the file.
	"""
	currentlist, lasthdr = _read_currentlist(fname, None)
	if len(currentlist) == 0:
		raise NoDataError, fname

	lc = len(currentlist)
	stepperstates = []
	nsamp = min(Nsamp, int(lc*(1.0-tail)))	# How many samples to extract?
	assert nsamp > 0
	for i in range(nsamp):
		f = float(i)/float(nsamp)
		aCurrent = currentlist[int((tail + (1.0-tail)*f)*lc)]
		stepperstate = {}
		lc = len(currentlist)
		assert lc > 0
		for (k, v) in aCurrent.items():
			# This is iterating over the various utterances.
			keymap = dict([(key, i) for (i, key) in enumerate(v.names)])
			stepperstate[k] = IC.index(keymap, p=v.prms(), name=str(k))
		stepperstates.append( stepperstate )
	return (lasthdr, stepperstates)


def read_multi_uid(fname, uid, Nsamp=10, tail=0.0, trigger=None):
	"""Read in a log file, selecting information only for a particular UID.
	This *doesn't* read in multiple UIDs, no matter what the name says:
	the "multi" refers to the fact that it gives you multiple samples
	from the log.   In other words, it provides a time-series of the changes
	to the parameters.

	@param Nsamp: the maximum number of samples to extract (or None, or -1).
		None means "as many as are available"; -1 means "as many samples as there are parameters."
	@type Nsamp: L{int} or L{None}.
	@param tail: Where to start in the file?
		C{tail=0} means that you start at the trigger or beginning.
		C{tail=1-epsilon} means you take just the last tiny bit of the file.
	@except NoDataError: When the log file is empty or a trigger is set but not triggered.
	"""
	currentlist, lasthdr = _read_currentlist(fname, trigger)
	if len(currentlist) == 0:
		raise NoDataError, fname

	lc = len(currentlist)
	tail = min(tail, 1.0 - 0.5/lc)
	indexers = []
	nsamp = lc-int(lc*tail)	# How many samples to extract?
	if Nsamp is not None and Nsamp == -1:
		Nsamp = currentlist[0][uid].prms().shape[0]
		assert Nsamp > 0
		if Nsamp < nsamp:
			nsamp = Nsamp
	elif Nsamp is not None and Nsamp < nsamp:
		nsamp = Nsamp
	print '# len(currentlist)=', len(currentlist), 'tail=', tail, 'nsamp=', nsamp
	assert nsamp > 0
	# logps = []
	logps = numpy.zeros((nsamp,))
	for i in range(nsamp):
		f = float(i)/float(nsamp)
		aCurrent = currentlist[int((tail + (1.0-tail)*f)*lc)]
		assert len(currentlist) > 0
		keymap = dict([(key, j) for (j, key) in enumerate(aCurrent[uid].names)])
		indexers.append(
			IC.index(keymap, p=aCurrent[uid].prms(), name=uid)
			)
		# logps.append( aCurrent[uid].logp() )
		# logps[i] = aCurrent[uid].logp()
		logps.itemset(i, aCurrent[uid].logp())
	# print '#logps=', logps
	return (lasthdr, indexers, logps)


def read_human_fmt(fname):
	"""This reads a more human-readable format, as produced by L{print_log}.
	It can easily be modified with a text editor to change parameters.
	"""
	statedict = {}
	logps = {}
	hdr = {}
	lnum = 0
	uid = None
	map = {}
	prms = []
	for line in open(fname, 'r'):
		if not line.endswith('\n'):
			die.warn("Incomplete line - no newline: %d" % (lnum+1))
			continue
		lnum += 1
		line = line.strip()
		if line == '':
			continue
		elif line.startswith('#'):
			tmp = avio.parse(line[1:])

			if 'uid' in tmp:
				if uid is not None:
					statedict[uid] = IC.index(map, p=numpy.array(prms, numpy.float), name=uid)
					map = {}
					prms = []
				uid = tmp['uid']
				if uid in statedict:
					raise BadFormatError, "human format: duplicate uid=%s" % uid
				if 'logP' in tmp:
					logps[uid] = float(tmp['logP'])
			else:
				hdr.update(tmp)
		else:
			cols = line.strip().split(None, 1)
			print 'line=', line, 'cols=', cols
			if len(cols) != 2:
				raise BadFormatError, "human format: needs two columns line %d" % lnum
			map[IC.index_base._unfmt(cols[1])] = len(prms)
			try:
				prms.append( float(cols[0]) )
			except ValueError:
				raise BadFormatError, "human format: need number in first column line %d: %s" % (lnum, cols[0])
	statedict[uid] = IC.index(map, p=numpy.array(prms, numpy.float), name=uid)

	return (hdr, statedict, logps)


def load_module(phdr):
	try:
		m = load_mod.load_named(os.path.splitext(phdr['model_file'])[0])
	except ImportError:
		m = None
	if m is None:
		m = load_mod.load_named(phdr['model_name'])
	return m


def print_log(fname, which):
	try:
		hdr, stepperstate, vlists, logps = read_log(fname, which)
	except BadFormatError, x:
		die.info("Not main log format: %s" % str(x))
		hdr, stepperstate, logps = read_human_fmt(fname)
		vlists = None
	for (k, v) in sorted(hdr.items()):
		print '#', avio.concoct({k: v})
	for (uid, v) in sorted(stepperstate.items()):
		print '#', avio.concoct({'uid': uid, 'logP': logps[uid]})
		for (i, pkey, p) in  sorted(v.i_k_val()):
			print p, v._fmt(pkey)
		print


if __name__ == '__main__':
	import sys
	which = 'last'
	arglist = sys.argv[1:]
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-last':
			which = 'last'
		elif arg == '-best':
			which = 'best'
		elif arg == '-frac':
			which = 'frac%f' % float(arglist.pop(0))
		elif arg == '-index':
			which = 'index%d' % int(arglist.pop(0))
		else:
			die.die('Unrecognized arg: %s' % arg)
	assert len(arglist) == 1
	fname = arglist.pop(0)
	print_log(fname, which)

