"""This a helper module for multivariance.py"""


import multivariance_classes as M
import Num
import random
import gpkmisc

HUGE = 1e30

class quadratic(M.modeldesc):
	__doc__ = """This describes a quadratic model of a known size."""

	def __init__(self, dataset=None, ndim=None):
		assert (dataset is not None) != (ndim is not None)
		if dataset is not None:
			ndim = len(dataset[0])
		M.modeldesc.__init__(self, ndim)


	def modeldim(self):
		m = self.ndim()
		return m + (m*(m+1))/2



	def unpack(self, prms):
		m = self.ndim()
		assert len(prms) == self.modeldim()
		mu = prms[:m]
		invsigma = Num.zeros((m, m), Num.Float)
		j = m
		for i in range(m):
			tmp = prms[j:j+(m-i)]
			invsigma[i,i:] = tmp
			invsigma[i:,i] = tmp
			j += m-i
		return self.new(mu, invsigma)

	def new(self, mu, invsigma, bias=0.0):
		return quadratic_with_numbers(mu, invsigma, self, bias)

	def start(self, data):
		"""Returns (starting position vector, covariance matrix)"""
		n = self.ndim()
		if len(data) > 1:
			iv = M.diag_inv_variance(data)
		else:
			iv = Num.identity(n)

		ivd = Num.diagonal(iv)
		isd = Num.sqrt(ivd)
		size = []
		tmp = []
		for i in range(n):
			for j in range(i,n):
				size.append(isd[i]*isd[j])
			tmp.append(iv[i,i:])
		packedivar = Num.concatenate( tmp )
		# print 'SIZE=', size
		packedvarivar = Num.array( size, copy=True )
		# print 'PIV', packedivar
		# print 'RCD', random.choice(data)
		packedpos = Num.concatenate( ( random.choice(data), packedivar ) )
		packedsize = Num.concatenate( (1.0/Num.diagonal(iv), packedvarivar) )

		return ( packedpos, gpkmisc.make_diag(packedsize) )




class quadratic_with_numbers(M.model_with_numbers):
	def __init__(self, mu, invsigma, details, bias=0.0, offset=None):
		"""self.mu, self.invsigma, and self._offset should be considered
		read-only for all users of this class."""
		assert isinstance(details, quadratic)
		M.model_with_numbers.__init__(self, details, bias)
		n = self.ndim()
		self.mu = Num.array(mu, copy=True)
		assert self.mu.shape == (n,)
		self.invsigma = Num.array(invsigma, copy=True)
		assert self.invsigma.shape == (n,n)
		self._offset = offset

	def __str__(self):
		return '<quadratic: mu=%s; invsigma=%s >' % (str(self.mu), str(self.invsigma))

	__repr__ = __str__

	addoff = M._q_addoff	# Will not be called if _offset is not None



	def logp(self, datum):
		delta = datum - self.mu
		parab = Num.dot(delta, Num.matrixmultiply(self.invsigma,
							delta))
		if not parab >= 0.0:
			raise M.QuadraticNotNormalizable, "Not positive-definite"
		return -parab/2.0 + self.offset() + self.bias

	



class diag_quadratic(quadratic):
	def __init__(self, dataset=None, ndim=None):
		quadratic.__init__(self, dataset, ndim)


	def modeldim(self):
		m = self.ndim()
		return 2*m


	def unpack(self, prms):
		m = self.ndim()
		assert len(prms) == self.modeldim()
		mu = prms[:m]
		invsigma = prms[m:]
		return self.new(mu, invsigma)

	def new(self, mu, invsigma, bias=0.0):
		return diag_quadratic_with_numbers(mu, invsigma, self, bias)

	def start(self, data):
		if len(data) > 1:
			iv = M.vec_inv_variance(data)
		else:
			iv = Num.ones(self.ndim(), Num.Float)

		packeddata = Num.concatenate((random.choice(data), iv))
		packedsize = Num.concatenate((1.0/iv, iv**2))

		return ( packeddata,
			gpkmisc.make_diag(packedsize)
			)



class diag_quadratic_with_numbers(M.model_with_numbers):
	def __init__(self, mu, invsigma, details, bias=0.0, offset=None):
		assert isinstance(details, diag_quadratic)
		M.model_with_numbers.__init__(self, details, bias)
		self.mu = Num.array(mu, copy=True)
		self.invsigma = Num.array(invsigma, copy=True)
		n = self.ndim()
		assert self.invsigma.shape == (n,)
		assert self.mu.shape == (n,)
		self._offset = offset

	def __str__(self):
		return '<diag-quadratic: mu=%s; invsigma=%s >' % (str(self.mu), str(self.invsigma))

	__repr__ = __str__

	addoff = M._d_addoff	# Will not be called if _offset is not None

	def logp(self, datum):
		delta = datum - self.mu
		parab = Num.sum(self.invsigma * delta**2)
		if not parab >= 0.0:
			raise M.QuadraticNotNormalizable, "Not positive-definite"
		return -parab/2.0 + self.offset() + self.bias
