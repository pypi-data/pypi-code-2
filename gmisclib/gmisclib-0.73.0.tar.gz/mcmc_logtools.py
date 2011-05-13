
import math
import numpy

import die
import Numeric_gpk as NG
import mcmc_logger

import mcmc_newlogger as LG



FILE_DROP_FAC = 0.2
TRIGGER = 'run_to_bottom finished'


def read_many_files(fnames, uid, Nsamp, tail, trigger):
	"""
	@return: a dictionary mapping filenames onto "data" and header information.
		Header information is from the last file read.
		The "data" are L{onelog} class instances that encapsulate
		log information from one log file.
	@rtype: tuple(dict(str:onelog), dict(str:str))
	"""
	hdr = {}
	per_fn = {}
	if uid is None:
		for fname in fnames:
			hdr, indexers, logps = mcmc_logger.read_multisample(fname, Nsamp=Nsamp, tail=tail, trigger=trigger)
			per_fn[fname] = onelog(logps, indexers, fname)
	else:
		for fname in fnames:
			try:
				hdr, indexers, logps = LG.read_multi_uid(fname, uid,
									Nsamp=Nsamp, tail=tail,
									trigger=trigger
									)
			except LG.BadFormatError, x:
				try:
					hdr, statedict, logps = LG.read_human_fmt(fname)
				except LG.BadFormatError, y:
					raise LG.BadFormatError, "Unreadable in either format: {%s} or {%s}" % (x, y)
				try:
					indexers = [statedict[uid]]
					logps = [logps[uid]]
				except KeyError:
					raise LG.BadFormatError, "human format: uid=%s not found" % uid
				else:
					per_fn[fname] = onelog(logps, indexers, fname)
	
			except LG.NoDataError, x:
				die.warn("No data in %s: %s" % (fname, x))
			else:
				per_fn[fname] = onelog(logps, indexers, fname)
	return (per_fn, hdr)



def get_pmap(per_fn):
	for ol in per_fn.values():
		return ol.indexers[0].map
	raise ValueError, "No data - cannot get_pmap."


def indexer_covar(per_fn, sample_selector):
	idxr_map = get_pmap(per_fn)
	ndim = len(idxr_map)
	sum = numpy.zeros((ndim,))
	sw = 0
	for (ol, i) in sample_selector(per_fn):
		idxr = ol.indexers[i]
		numpy.add(sum, idxr.get_prms(), sum)
		sw += 1
	assert sw > 0
	m = sum/sw

	sum = numpy.zeros((ndim, ndim))
	for (ol, i) in sample_selector(per_fn):
		idxr = ol.indexers[i]
		delta = idxr.get_prms() - m
		assert len(delta.shape) == 1
		delta2 = numpy.outer(delta, delta)
		assert len(delta2.shape) == 2
		numpy.add(sum, delta2, sum)
	if sw > 1:
		var = sum/(sw-1)
	else:
		var = None
	return (m, var, sw, idxr_map)


def logp_stdev(per_fn, sample_selector):
	sw = 0
	slp = 0.0
	for (ol, i) in sample_selector(per_fn):
		slp += ol.logps.item(i)
		sw += 1
	assert sw > 0, "No data in average in logp_stdev"
	lpavg = slp/sw
	n = sw
	svar = 0.0
	for (ol, i) in sample_selector(per_fn):
		svar += (ol.logps.item(i) - lpavg)**2
	if sw > 1:
		return (('logp',), lpavg, math.sqrt((svar/sw)*float(n)/float(n-1)) )
	return (('logp',), lpavg, None)


def after_convergence(per_fn):
	"""This selects which measurements will be used."""
	for ol in per_fn.values():
		if ol.convergence is not None:
			for i in range(ol.convergence, len(ol.indexers)):
				yield (ol, i)


def some_after_convergence(per_fn):
	"""This selects which measurements will be used.
	It looks after convergence, then throws out optimizations that haven't
	converged.
	"""
	maxes = []
	for ol in per_fn.values():
		if ol.convergence is not None:
			maxes.append( NG.N_maximum(ol.logps[ol.convergence:]) )
	ndim = len(get_pmap(per_fn))
	assert ndim > 0
	tol = 6 * math.sqrt(ndim)
	threshold = max(maxes) - tol
	for ol in per_fn.values():
		if ol.convergence is not None:
			for i in range(ol.convergence, len(ol.indexers)):
				if ol.logps.item(i) > threshold:
					yield (ol, i)

def near_each_max(per_fn):
	"""This selects which measurements will be used.
	It looks after convergence, then gives you the best few
	results from each run.
	"""
	ndim = len(get_pmap(per_fn))
	assert ndim > 0
	tol = 6 * math.sqrt(ndim)
	for ol in per_fn.values():
		if ol.convergence is not None:
			themax = NG.N_maximum(ol.logps[ol.convergence:])
			threshold = themax - tol
			for i in range(ol.convergence, len(ol.indexers)):
				if ol.logps.item(i) > threshold:
					yield (ol, i)


def all(per_fn):
	"""This selects which measurements will be used."""
	for ol in per_fn.values():
		for i in range(len(ol.indexers)):
			yield (ol, i)


def last(per_fn):
	"""This selects which measurements will be used."""
	for ol in per_fn.values():
		assert isinstance(ol, onelog)
		yield (ol, len(ol.indexers)-1)


def each_best(per_fn):
	"""This selects which measurements will be used."""
	for ol in per_fn.values():
		if ol.convergence is not None:
			bi = numpy.argmax(ol.logps[ol.convergence:]) + ol.convergence
			yield (ol, bi)



def overall_best(per_fn):
	"""This selects which measurements will be used."""
	blp = None
	bol = None
	bi = None
	for (ol, i) in each_best(per_fn):
		if blp is None or ol.logps.item(i) > blp:
			blp = ol.logps.item(i)
			bol = ol
			bi = i
	yield (bol, bi)




def indexer_stdev(per_fn, selector):
	"""Return a summary of the properties of the last indexer in each file."""
	mean, covar, n, idxr_map = indexer_covar(per_fn, selector)
	o = []
	for (nm, i) in idxr_map.items():
		if covar is None:
			std = None
		else:
			std = math.sqrt(covar[i,i])
		o.append( (nm, mean[i], std) )
	return o


def print_index_error(ke):
	print 'Cannot find key= %s in index.' % str(ke.args[0])
	idxr = ke.args[1]
	kl = sorted(idxr.map.keys())
	print 'The index has these keys:'
	for k in kl:
		print 'Key=', idxr._fmt(k)




class onelog:
	def __init__(self, logps, indexers, fname):
		assert len(indexers) == len(logps)
		assert isinstance(logps, numpy.ndarray)
		assert isinstance(indexers, list)
		self.logps = logps
		self.indexers = indexers
		self.fname = fname
		self.convergence = None





def estimate_convergence(per_fn, FileDropFac, Trim=None, Stretch=None):
	mxvs = []
	for (k, ol) in per_fn.items():
		mxvs.append( (max(ol.logps), k) )
	mxvs.sort()
	for (lp, kk) in mxvs:
		print '# max(%s) = %g' % (kk, lp)
	ndrop = int(math.floor(FileDropFac * len(per_fn)))
	keep = [k for (mxlogp, k) in mxvs[ndrop:]]
	for kk in keep:
		per_fn[kk].convergence = 0


def ascii_cmp(a, b):
	"""Compares the ASCII form of keys, for sorting purposes.   Does a good
	attempt at ASCII ordering for strings and numeric ordering for numbers.
	"""
	asp = a.split(',')
	bsp = b.split(',')
	return key_cmp(asp, bsp)


def key_cmp(a, b):
	"""Compares the tuple form of keys, for sorting purposes.   Does a good
	attempt at ASCII ordering for strings and numeric ordering for numbers.
	"""
	for (aa, bb) in zip(a, b):
		for fcn in [float, str]:
			try:
				c = cmp(fcn(aa), fcn(bb))
				if c != 0:
					return c
				break	# c==0
			except ValueError:
				pass
	return 0
