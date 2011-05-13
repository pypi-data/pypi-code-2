import re
import math
import random
import numpy

import mcmc	# from gmisclib

class probdist_c(object):
	def __call__(self):
		"""Sample from the probability distribution.
		@return: the sample
		@rtype: C{float}
		"""
		raise RuntimeError, "Virtual function"

	def logdens(self, x):
		"""Return the log(density) of the probability distribution at x.
		@param x: the position where the density should be evaluated.
		@type x: C{float}
		@return: C{log(density)}
		@rtype: C{float}
		@raise mcmc.NotGoodPosition: when the density is not defined at C{x}.
		"""
		raise RuntimeError, "Virtual function"


class Weibull(probdist_c):
	"""Weibull distribution"""
	def __init__(self, scale, shape):
		assert shape >= 0.0 and scale>=0.0
		self.shape = shape
		self.scale = scale
	
	def __call__(self):
		return random.weibullvariate(self.scale, self.shape)
	
	def logdens(self, x):
		assert x >= 0.0
		x /= self.scale
		return -x**self.shape + math.log(x)*(self.shape-1) +math.log(self.shape/self.scale)

	@property
	def __doc__(self):
		return "Weibull(%g,%s)" % (self.scale, self.shape)


class Expo(probdist_c):
	"""Exponential distribution"""

	def __init__(self, lmbda):
		assert lmbda > 0.0
		self.lmbda = lmbda

	def __call__(self):
		return random.expovariate(self.lmbda)

	def logdens(self, x):
		if x < 0.0:
			raise mcmc.NotGoodPosition, "x=%s" % str(x)
		assert x >= 0.0
		return -self.lmbda*x + math.log(self.lmbda)

	@property
	def __doc__(self):
		return "Exponential(%g)" % self.lmbda


class Normal(probdist_c):
	"""Normal distribution"""

	def __init__(self, mu, sigma):
		if sigma <= 0.0:
			raise mcmc.NotGoodPosition, "sigma=%s" % str(sigma)
		self.mu = mu
		self.sigma = sigma

	def __call__(self):
		return random.normalvariate(self.mu, self.sigma)

	def logdens(self, x):
		return -(((x-self.mu)/self.sigma)**2)/2.0 - math.log(math.sqrt(2*math.pi)*self.sigma)

	@property
	def __doc__(self):
		return "Normal(%g+-%g)" % (self.mu, self.sigma)



class Uniform(probdist_c):
	"""Uniform distribution"""
	def __init__(self, low, high):
		if not (low < high):
			raise mcmc.NotGoodPosition, "low=%s >= high=%s" % (low, high)
		self.low = low
		self.high = high

	def __call__(self):
		return random.uniform(self.low, self.high)

	def logdens(self, x):
		return 1.0/(self.high-self.low)

	@property
	def __doc__(self):
		return "Uniform(%g,%g)" % (self.low, self.high)


class LogNormal(probdist_c):
	"""Lognormal distribution"""
	def __init__(self, mu, sigma):
		if sigma <= 0.0:
			raise mcmc.NotGoodPosition, "sigma=%s" % str(sigma)
		self.mu = mu
		self.sigma = sigma

	def __call__(self):
		return self.mu*math.exp(random.normalvariate(0.0, self.sigma))

	def logdens(self, x):
		if (x>0.0) != (self.mu>0.0):
			raise mcmc.NotGoodPosition, "x=%s, mu=%s" % (str(x), str(self.mu))
		x = math.log(x/self.mu)
		return -((x/self.sigma)**2)/2.0 - math.log(math.sqrt(2*math.pi)*self.sigma)

	@property
	def __doc__(self):
		return "Lognormal(%g+-%g)" % (self.mu, self.sigma)


def logp_prior_normalized(x, guess_prob_dist):
	"""
	@type guess_prob_dist: list((str, probdist_c))
	@type x: newstem2.indexclass.index_base
	@rtype: float
	@return: the log of the prior probability.
	"""
	lp = 0.0
	gpd = [ (re.compile(pat), sampler) for (pat, sampler) in guess_prob_dist]
	for key in x.map.keys():
		v = x.p(*key)

		vv = None
		fkey = x._fmt(key)
		for (pat, sampler) in gpd:
			if pat.match(fkey):
				vv = sampler
				break
		if vv is None:
			raise KeyError, "No match found for '%s'" % fkey
		logp = vv.logdens(v)
		# print 'prior(%s;%g)=%g' % (fkey, v, logp)
		lp += logp
	return lp


class problem_definition(mcmc.problem_definition):
	def __init__(self ):
		mcmc.problem_definition.__init__(self)
		self.idxr = None
		self.cached = -1e30
		self.ckey = None


	def set_idxr(self, idxr):
		self.idxr = idxr


	def plot(self, idxr, arg, pylab, inum):
		raise RuntimeError, "Virtual Function"


	def do_print(self, idxr, arg, iter):
		raise RuntimeError, "Virtual Function"


	def logp(self, x):
		assert self.idxr is not None, "You need to call self.set_idxr()."
		if self.ckey is not None and numpy.equal(self.ckey, x).all():
			return self.cached
		self.idxr.clear()
		self.idxr.set_prms(x)
		prob, constraint, logprior = self.logp_guts(self.idxr)
		self.cached = prob - constraint + logprior
		self.ckey = numpy.array(self.idxr.get_prms(), copy=True)
		return self.cached


	def logp_data_normalized(self, x):
		"""Only define this if you can compute the actual probability
		density for the data given model & parameters,
		not just something proportional to it!
		To do this
		function, you need to be able to do the full multidimensional
		integral over the probability distribution!

		NOTE that x is an indexer!
		NOTE that this is not the full logp function: it doesn't contain the prior!
		"""
		prob, constraint, logprior = self.logp_guts(x)
		return prob


	def fixer(self, x):
		assert self.idxr is not None, "You need to call self.set_idxr()."
		# print 'fixer in', hash(x.tostring())
		# print '\tPrms', ' '.join(['%.3f' % q for q in x])
		self.idxr.set_prms(x)
		prob, constraint, logprior = self.logp_guts(self.idxr)
		# print '\tProb, constraint', prob, constraint
		self.cached = prob - constraint + logprior
		self.ckey = numpy.array(self.idxr.get_prms(), copy=True)
		# print 'fixer out', hash(self.ckey.tostring())
		return self.ckey


	def logp_prior_normalized(self, x):
		return logp_prior_normalized(x, self.PriorProbDist)

	PriorProbDist = None	#: Data for guessing.

	def logp_guts(self, idxr, data_sink=None):
		raise RuntimeError, "Virtual method"

