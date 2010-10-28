import re
import math
import random

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


class Expo(probdist_c):
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


class Normal(probdist_c):
	def __init__(self, mu, sigma):
		if sigma <= 0.0:
			raise mcmc.NotGoodPosition, "sigma=%s" % str(sigma)
		self.mu = mu
		self.sigma = sigma

	def __call__(self):
		return random.normalvariate(self.mu, self.sigma)

	def logdens(self, x):
		return -(((x-self.mu)/self.sigma)**2)/2.0 - math.log(math.sqrt(2*math.pi)*self.sigma)



class Uniform(probdist_c):
	def __init__(self, low, high):
		if not (low < high):
			raise mcmc.NotGoodPosition, "low=%s >= high=%s" % (low, high)
		self.low = low
		self.high = high

	def __call__(self):
		return random.uniform(self.low, self.high)

	def logdens(self, x):
		return 1.0/(self.high-self.low)


class LogNormal(probdist_c):
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

