"""Support module for multivariance.py"""

from gmisclib import gpkmisc
from gmisclib import Num
from gmisclib import die


BAYES_PRIOR_SPACE = 0	# 1 for a flat prior in sigma,
HUGE = 1e30

class QuadraticNotNormalizable(ValueError):
	def __init__(self, s=''):
		ValueError.__init__(self, s)





def vec_inv_variance(start):
	vv = gpkmisc.vec_variance(start)
	assert Num.alltrue(Num.greater(vv, 0.0))
	return 1.0/vv


def diag_inv_variance(start):
	return gpkmisc.make_diag(vec_inv_variance(start))



class modeldesc:
	__doc__ = """Virtual base class for a description of a model
			of a particular size."""

	LF = (1.0/3.0)**2

	def __init__(self, ndim):
		assert ndim > 0
		self.dim = ndim

	def ndim(self):
		"""This returns the dimensionality of the data."""
		return self.dim

	def modeldim(self):
		"""This gives the dimensionality of the model,
		i.e. the number of parameters required to specify
		the means and covariance matrix(ces)."""
		raise RuntimeError, 'Virtual method'

	def unpack(self, prms):
		"""This returns some subclass of model."""
		raise RuntimeError, 'Virtual method'

	def new(self, mu, invsigma):
		"""Creates a model that contains data."""
		raise RuntimeError, 'Virtual method'

	def start(self, dataset):
		"""Selects a random starting point from the dataset."""
		raise RuntimeError, 'Virtual method'



class model_with_numbers:
	__doc__ = """Virtual base class for adding in the functions
		you need when you create a model with known parameters
		(like mu and sigma)."""

	def __init__(self, details, bias):
		"""Bias is an overall shift of the log probability up or
		down.  In a classifier, it is used to bias things toward
		one class or another."""
		self.desc = details
		self._offset = None
		self.bias = bias

	def logp(self, datum):
		raise RuntimeError, 'Virtual method'

	def pack(self):
		"""Returns a vector of parameters."""
		raise RuntimeError, 'Virtual method'

	def ndim(self):
		return self.desc.ndim()

	def unpack(self, prms):
		return self.desc.unpack(prms)

	def new(self, mu, invsigma):
		return self.desc.new(mu, invsigma)

	def start(self, dataset):
		return self.desc.start(dataset)

	def offset(self):
		if self._offset is None:
			self.addoff()
		return self._offset

	def addoff(self):	# Should not be called if _offset is not None
		raise RuntimeError, 'Virtual Function'






def _q_addoff(self):	# Will not be called if _offset is not None
	phasespacefac = BAYES_PRIOR_SPACE+1
	determinantfac = 1 - phasespacefac
	trace = Num.sum(Num.diagonal(self.invsigma))
	if trace <= 0.0:
		raise QuadraticNotNormalizable, "Input trace is nonpositive."
	try:
		self.ev = Num.LA.Heigenvalues(self.invsigma)
	except Num.LA.LinAlgError, x:
		die.warn('While computing the volume of the probability distribution: %s' % str(x))
		raise QuadraticNotNormalizable, x
	if not Num.alltrue(self.ev > 0.0):
		raise QuadraticNotNormalizable, "Some eigenvalues are zero or negative."
	assert abs(Num.sum(self.ev)-trace) < 1e-10 + 1e-6*trace, "Bad Eigenvalues run: trace not matched: %g to %g" % (trace, Num.sum(self.ev))
	assert Num.sum(self.ev) > 0.0, "Input trace is nonpositive."
	self._offset = Num.sum(Num.log(self.ev))*determinantfac



def _d_addoff(self):	# Will not be called if _offset is not None
	phasespacefac = BAYES_PRIOR_SPACE+1
	determinantfac = 1 - phasespacefac
	self.ev = Num.array(self.invsigma, copy=True)
	if not Num.alltrue(self.ev > 0.0):
		raise QuadraticNotNormalizable, "Some eigenvalues are zero or negative."
	self._offset = Num.sum(Num.log(self.ev))*determinantfac



