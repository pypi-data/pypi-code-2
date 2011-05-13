import math
import numpy
import gmisclib.Numeric_gpk as NG

_Float = numpy.dtype('float')

class lls_base(object):
	def __init__(self, a, copy=True):
		self.ginv = None
		self._fit = None
		self._x = None
		self._hatdiag = None
		self._y = None
		self.a = numpy.array(a, _Float, copy=copy)
		if self.a.ndim != 2:
			raise ValueError, "a needs to be 2-dimensional: shape=%s" % str(self.a.shape)
		self.m, self.n = self.a.shape
		self.q = None


	def set_y(self, y, copy=True):
		if y is None:
			return
		self._fit = None
		self._x = None
		self._y = numpy.array(y, _Float, copy=copy)
		if self._y.ndim == 1:	# Vector
			self.vector = True
			self._y = self._y.reshape((self._y.shape[0], 1))
			# self._y = numpy.transpose( [y] )
		elif self._y.ndim > 2:
			raise ValueError, "y needs to be 1- or 2-dimensional: shape=%s" % str(self._y.shape)
		else:
			self.vector = False
		if self._y.shape[0] != self.m:
			raise ValueError, "Matrix sizes do not match: (%d,%d) and %s" % (
								self.m, self.n, str(self._y.shape)
								)
		self.q = self._y.shape[1]


	def y(self, copy=True):
		assert self._y.shape == (self.m, self.q)
		if self.vector:
			return numpy.array(self._y[:,0], copy=copy)
		return numpy.array(self._y, copy=copy)



	def _solve(self):
		raise RuntimeError, "Virtual Function"


	def hat(self, copy=True):
		raise RuntimeError, "Virtual Function"


	def x(self, y=None, copy=True):
		"""
		@except numpy.linalg.linalg.LinAlgError: when the matrix is singular.
		"""
		self.set_y(y)
		assert self._y is not None, "Y not yet set"
		if self._x is None:
			self._x = self._solve()
		if self.vector:	# Restore everything to vectors
			return numpy.array(self._x[:, 0], copy=copy)
		return numpy.array(self._x, copy=copy)


	def fit(self, copy=False):
		"""
		@except numpy.linalg.linalg.LinAlgError: when the matrix is singular.
		"""
		if self._fit is None:
			if self._x is None:
				self._x = self._solve()
			# print 'fit from ', self.a.shape, self._x.shape
			self._fit = numpy.dot(self.a, self._x)
		# print 'fit.shape=', self._fit.shape, self.m, self.q
		assert self._fit.shape == (self.m, self.q)
		if self.vector:	# Restore everything to vectors
			return numpy.array(self._fit[:, 0], copy=copy)
		return numpy.array(self._fit, copy=copy)


	def residual(self):
		tmp = self.y(copy=False) - self.fit(copy=False)
		# print 'resid=', tmp
		assert tmp.shape[0] == self.m
		return tmp


	def variance_about_fit(self):
		"""Returns the estimator of the standard deviation
		of the data about the fit.
		@return: L{numpy.ndarray} with shape=(q,).   Each entry corresponds
			to one of the C{q} sets of equations that are being fit.
		"""
		r2 = numpy.sum(numpy.square(self.residual()), axis=0)
		assert self.vector and r2.shape==() or not self.vector and r2.shape==(self.q,)
		return r2/(self.m-self.n)

	def eff_n(self):
		"""Returns something like the number of data, except that it looks at their
		weighting and the structure of the problem.  It counts how many data have a
		relatively large effect on the solution, and if a datum has little influence,
		it doesn't count for much.
		@rtype: float
		"""
		return _perplexity(self.hat())
	
	def eff_rank(self):
		"""Returns something like the rank of the solution, but rather than counting
		how many dimensions can be solved at all, it reports how many dimensions can be
		solved with a relatively good accuracy.
		@rtype: float
		"""
		raise RuntimeError, "Virtual Method"



def _perplexity(p):
	numpy.divide(p, numpy.sum(p), p)
	p = numpy.compress(numpy.greater(p, 0.0), p)
	return math.exp(-numpy.sum(p*numpy.log(p)))



class linear_least_squares(lls_base):
	def __init__(self, a, y=None, minsv=None, minsvr=None, copy=True):
		"""This solves the set of linear equations a*x = y,
		and allows you to get properties of the fit via methods.
		Normally, a.shape==(m,n) and y.shape==(m,q),
		and the returned x.shape==(n,q).
		where m is the number of constraints provided by the data,
		n is the number of parameters to use in a fit
		(equivalently, the number of basis functions),
		and q is the number of separate sets of equations
		that you are fitting.
		Then, C{self.x()} has shape (n,q) and C{self.the_fit()} has shape (m,q).
		Interpreting this as a linear regression, there are n
		parameters in the model, and m measurements.
		Q is the number of times you apply the model to a
		different data set; each on yields a different solution.
	
		The procedure uses a singular value decomposition algorithm,
		and treats all singular values that are smaller than minsv
		as zero (i.e. drops them). 
		If minsvr is specified, it treates all singular values that
		are smaller than minsvr times the largest s.v. as zero.
		The returned rank is the
		rank of the solution, which is normally the number of
		nonzero elements in x.
		Note that the shape of the solution vector or matrix
		is defined by a and y, and the rank can be smaller
		than m.
	
		@note: Y may be a 1-D matrix (a vector), in which case
			the fit is a vector.    This is the normal
			case where you are fitting one equation.
			If y is a 2-D matrix,
			each column (second index) in y is a separate fit, and
			each column in the solution is a separate result.
		"""
	
		lls_base.__init__(self, a, copy=copy)
		self.set_y(y, copy=copy)

		assert minsv is None or minsv >= 0.0
		assert minsvr is None or 0.0 <= minsvr <= 1.0
		r = min(self.m, self.n)
		if self.n > 0:
			u, self.s, vh = numpy.linalg.svd(self.a, full_matrices=False)
		else:
			u = numpy.zeros((self.m, r))
			vh = numpy.zeros((r, self.n))
			self.s = numpy.zeros((r,))
		# assert u.shape == (self.m, self.m)
		assert u.shape == (self.m, r)
		# assert vh.shape == (self.n, self.n)
		assert vh.shape == (r, self.n)
		assert self.s.shape == (r,)
		# rbasis = numpy.dot(numpy.dot(u, sigma), vh)
		# rbasis = numpy.dot(u[:,:r]*self.s, vh[:r])
		# rbasis = numpy.dot(u[:,:r], self.s*vh)
		# print 'rbasis=', rbasis
		# assert numpy.sum(numpy.square(rbasis-a)) < 0.0001*numpy.sum(numpy.square(self.a))
		if minsv is not None and minsvr is not None:
			svrls = max(minsv, minsvr*self.s[numpy.argmax(self.s)] )
		elif minsv is not None:
			svrls = minsv
		elif minsvr is not None and self.s.shape[0]>0:
			svrls = minsvr * self.s[numpy.argmax(self.s)]
		else:
			svrls = 0.0
	
		self.sim = numpy.greater(self.s, svrls)
		isi = numpy.where(self.sim, 1.0/numpy.where(self.sim, self.s, 1.0), 0.0)
		# self.ginv = numpy.dot(u[:,:r]*isi, vh[:r]).transpose()
		ur = u[:,:r]
		numpy.multiply(ur, isi, ur)
		# self.ginv = numpy.transpose(numpy.dot(u[:,:r]*isi, vh[:r]))
		self.ginv = numpy.dot(ur, vh[:r]).transpose()

	def _solve(self):
		return numpy.dot(self.ginv, self._y)

	def sv(self):
		return self.s

	def rank(self):
		return self.sim.sum()

	def hat(self, copy=True):
		"""Hat Matrix Diagonal
		Data points that are far from the centroid of the X-space are potentially influential.
		A measure of the distance between a data point, xi,
		and the centroid of the X-space is the data point's associated diagonal
		element hi in the hat matrix. Belsley, Kuh, and Welsch (1980) propose a cutoff of
		2 p/n for the diagonal elements of the hat matrix, where n is the number
		of observations used to fit the model, and p is the number of parameters in the model.
		Observations with hi values above this cutoff should be investigated.
		For linear models, the hat matrix

		C{H = X inv(X'X) X'}

		can be used as a projection matrix.
		The hat matrix diagonal variable contains the diagonal elements
		of the hat matrix

		C{hi = xi inv(X'X) xi'}
		"""
		if self._hatdiag is None:
			aainv = numpy.dot(self.ginv, self.ginv.transpose())
			hatdiag = numpy.zeros((self.a.shape[0],), _Float)
			for i in range(hatdiag.shape[0]):
				hatdiag[i] = NG.qform(self.a[i,:], aainv)
				assert -0.001 < hatdiag[i] < 1.001
			self._hatdiag = hatdiag
		return numpy.array(self._hatdiag, copy=copy)


	def x_variances(self):
		"""Estimated standard deviations of the solution.
		This is the diagonal of the solution covariance matrix.
		"""
		aainv = numpy.dot(self.ginv, self.ginv.transpose())
		vaf = self.variance_about_fit()
		rv = numpy.outer(aainv.diagonal(), vaf)
		assert rv.shape == self._x.shape
		assert rv.shape == (self.n, self.q)
		if self.vector:
			return rv[0,:]
		return rv

	def eff_rank(self):
		return _perplexity(self.sv())



class reg_linear_least_squares(lls_base):
	def __init__(self, a, y, regstr=0.0, regtgt=None, rscale=None, copy=True):
		"""This solves min! |a*x - y|^2 + |regstr*(x-regtgt)|^2,
		and returns (x, the_fit, rank, s).
		Normally, a.shape==(m,n) and y.shape==(m,q),
		where m is the number of data to be fit,
		n is the number of parameters to use in a fit
		(equivalently, the number of basis functions),
		and q is the number of separate sets of equations
		that you are fitting.
		Then, x has shape (n,q) and the_fit has shape (m,q).
	
		The regularization target,
		regtgt is the same shape as x, that is (n,q).
		(It must be a vector if and only if y is a vector.)
		Regstr, the strength of the regularization is
		normally an (n,n) matrix, though (*,n) will work,
		as will a scalar.
	
		Y may be a 1-D matrix (a vector), in which case
		the fit is a vector.    This is the normal
		case where you are fitting one equation.
		If y is a 2-D matrix,
		each column (second index) in y is a separate fit, and
		each column in the solution is a separate result.
		"""
		lls_base.__init__(self, a, copy=copy)
		self.set_y(y, copy=copy)

		if regtgt is None:
			self.regtgt = numpy.zeros((self.n, self.q))
		else:
			self.regtgt = numpy.array(regtgt, _Float, copy=copy)
		if self.vector:
			if regtgt.ndim != 1:
				raise ValueError, "regtgt must be a vector if y is a vector."
			self.regtgt = self.regtgt.reshape((regtgt.shape[0],1))
			# regtgt = numpy.transpose( [regtgt] )
		assert self.regtgt.ndim == 2, "Bad dimensionality for regtgt: %d" % self.regtgt.ndim
		if self.regtgt.shape[0] != self.n:
			raise ValueError, "Regtgt shape must match the shape of a"

		regstr = numpy.asarray(regstr, _Float)
		if regstr.ndim == 0:
			regstr = numpy.identity(self.n) * regstr
		assert regstr.ndim == 2, "Wrong dimensionality for regstr: %d" % regstr.ndim
		assert regstr.shape[1] == self.n
	
		self.rr = numpy.dot(regstr.transpose(), regstr)
		self.aa = numpy.dot(self.a.transpose(), self.a)
		if rscale is None:
			self.scale = 1.0
		else:
			self.scale = rscale * self.aa.trace()/self.rr.trace()
		# print 'aa=', self.aa
		# print 'rr=', self.rr
		# print 'traa', numpy.trace(self.aa)
		# print 'trrr', numpy.trace(self.rr)
		# print 'scale=', self.scale
		# print 'regtgt=', self.regtgt
		self.aareg = self.aa + self.rr*self.scale


	def _solve(self):
		"""
		@except numpy.linalg.linalg.LinAlgError: when the matrix is singular.
		"""
		ayreg = numpy.dot(self.a.transpose(), self._y)	\
				+ numpy.dot(self.rr, self.regtgt)*self.scale
		# print 'ayreg from', self.a.transpose().shape, '*', self._y.shape
		# print '+ayreg from', self.rr.shape, '*', self.regtgt.shape, '*', self.scale
		# print '_solve from', self.aareg.shape, ayreg.shape
		return numpy.linalg.solve(self.aareg, ayreg)
	

	def sv_reg(self):
		"""Singular values of the regularized problem."""
		return numpy.sqrt(numpy.linalg.eigvalsh(self.aareg))

	def sv_unreg(self):
		"""Singular values of the unregularized problem."""
		return numpy.sqrt(numpy.linalg.eigvalsh(self.aa))

	def eff_rank(self):
		return _perplexity(self.sv_reg())

	def hat(self, copy=True):
		"""Hat Matrix Diagonal
		Data points that are far from the centroid of the X-space are potentially influential.
		A measure of the distance between a data point, xi,
		and the centroid of the X-space is the data point's associated diagonal
		element hi in the hat matrix. Belsley, Kuh, and Welsch (1980) propose a cutoff of
		2 p/n for the diagonal elements of the hat matrix, where n is the number
		of observations used to fit the model, and p is the number of parameters in the model.
		Observations with hi values above this cutoff should be investigated.
		For linear models, the hat matrix

		C{H = X (X'X)-1 X' }

		can be used as a projection matrix.
		The hat matrix diagonal variable contains the diagonal elements
		of the hat matrix

		C{hi = xi (X'X)-1 xi' }
		"""
		if self._hatdiag is None:
			hatdiag = numpy.zeros((self.aa.shape[0],), _Float)
			iaareg = numpy.linalg.inv(self.aareg)
			for i in range(hatdiag.shape[0]):
				hatdiag[i] = NG.qform(self.a[i,:], iaareg)
				assert -0.001 < hatdiag[i] < 1.001
			self._hatdiag = hatdiag
		return numpy.array(self._hatdiag, copy=copy)




def test_svd():
	a0 = numpy.array([[0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, -3, -2, -1, 0, 1, 2, 3, 0, 0, 0, 0, 0],
		[0, 0, 0, 0, 0, 0, 0, 1, -1, 1, -1, 1, -1, 1, 0, 0, 0, 0, 0]], _Float)
	a1 = numpy.array([[1, 1, 1],
		[-3, -2, -1],
		[1, -1, 1]], _Float)
	a2 = numpy.array([[1, 1, 1], [-3, -2, -1], [1, -1, 1], [0, 0, 2.2], [2, 0, 0], [0, 1, 0]],
			_Float)
	for a in [a0, a1, a2]:
		u, s, vh = numpy.linalg.svd(a)
		r = min(a.shape)
		# print 'shapes for u,s, vh=', u[:,:r].shape, s.shape, vh[:r].shape, 'r=', r
		assert numpy.alltrue( s >= 0.0)
		err = numpy.sum(numpy.square(numpy.dot(u[:,:r]*s, vh[:r]) - a))
		assert err < 1e-6


def all_between(a, vec, b):
	return numpy.alltrue(
			numpy.greater_equal(vec, a)
			* numpy.greater_equal(b, vec)
			)

def test0():
	y = numpy.array([0, 1, 2, 3, 4, 5], numpy.float)
	basis = numpy.zeros((6,0))
	soln = linear_least_squares(basis, y, 1e-6)
	assert numpy.absolute(soln.fit()).sum() < 1e-4
	assert numpy.absolute(soln.residual()-y).sum() < 1e-4
	assert soln.rank() == 0
	assert soln.x().shape==(0,)


def test_vec():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], _Float)
	soln = linear_least_squares(basis, y, 1e-6)
	hat = soln.hat()
	assert numpy.alltrue(hat > 1.0/y.shape[0])
	assert numpy.alltrue(hat < 4.0/y.shape[0])
	assert soln.rank() == 2
	print 'fitshape=', soln.fit().shape, y.shape
	print 'y=', y
	print 'fit=', soln.fit()
	err = numpy.sum(numpy.square(soln.fit()-y))
	assert 0.0 <= err < 1e-6
	print 'soln.residual=', soln.residual()
	assert all_between(-1e-6, soln.residual(), 1e-6)
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0] - 1) < 1e-6
	assert abs(soln.x()[1] + 1) < 1e-6
	assert numpy.absolute(numpy.dot(basis, soln.x()) - soln.fit()).sum() < 1e-6


def test_vec2():
	basis = numpy.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
				[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.array([0, 2, 0, 2, 0, 2, 0, 2, 0, 2, 0], _Float)
	# This test is obsolete and needs to be fixed.
	soln = linear_least_squares(basis, y, 1e-6)
	assert soln.rank() == 2
	err = numpy.sum((soln.fit()-y)**2)
	avg = 10.0/11.0
	epred = 6.0*avg**2 + 5.0*(2-avg)**2
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[1] - avg) < 1e-6
	assert abs(soln.x()[0]) < 1e-6
	assert abs(err - epred) < 1e-4



def test_m1():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]])
	assert y.shape[1] == 1
	soln = linear_least_squares(basis, y, 1e-6)
	assert soln.x().shape[1] == 1
	assert soln.fit().shape[1] == 1
	assert soln.rank() == 2
	err = soln.residual()**2
	assert all_between(0, err, 1e-6)
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0,0] - 1) < 1e-6
	assert abs(soln.x()[1,0] + 1) < 1e-6
	assert numpy.absolute(numpy.ravel(numpy.dot(basis, soln.x())-y)).sum() < 1e-6


def test_m2():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]])
	assert y.shape[1] == 2
	soln = linear_least_squares(basis, y, 1e-6)
	assert soln.x().shape[1] == 2
	assert soln.fit().shape[1] == 2
	assert soln.rank() == 2
	err = numpy.sum((soln.fit()-y)**2, axis=0)
	assert err.shape[0]==2
	assert all_between(0.0, err, 1e-6)
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0,0] - 1) < 1e-6
	assert abs(soln.x()[1,0] + 1) < 1e-6
	assert abs(soln.x()[0,1] + 1) < 1e-6
	assert abs(soln.x()[1,1] - 10) < 1e-6
	assert numpy.absolute(numpy.ravel(numpy.dot(basis, soln.x())-y)).sum() < 1e-6


def test_m2r():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]])
	assert y.shape[1] == 2
	soln = reg_linear_least_squares(basis, y, numpy.zeros((2,2), _Float), [[0.0, 0.0], [0.0, 0.0]])
	hat = soln.hat()
	assert numpy.alltrue(hat > 1.0/y.shape[0])
	assert numpy.alltrue(hat < 4.0/y.shape[0])
	assert soln.x().shape[1] == 2
	assert soln.fit().shape[1] == 2
	err = numpy.sum((soln.fit()-y)**2, axis=0)
	assert err.shape[0]==2
	assert all_between(0.0, err, 1e-6)
	assert abs(soln.x()[0,0] - 1) < 1e-6
	assert abs(soln.x()[1,0] + 1) < 1e-6
	assert abs(soln.x()[0,1] + 1) < 1e-6
	assert abs(soln.x()[1,1] - 10) < 1e-6
	assert numpy.absolute(numpy.ravel(numpy.dot(basis, soln.x())-y)).sum() < 1e-6


def test_m2rR():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.transpose([[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]])
	assert y.shape[1] == 2
	soln = reg_linear_least_squares(basis, y, 1e6*numpy.identity(2), [[0.5, 0.5],[0.5,0.5]])
	assert soln.x().shape[1] == 2
	assert soln.fit().shape[1] == 2
	err = numpy.sum((soln.fit()-y)**2, axis=0)
	assert err.shape[0]==2
	assert all_between(1.0, err, 500.0)
	assert abs(soln.x()[0,0] - 0.5) < 1e-3
	assert abs(soln.x()[1,0] - 0.5) < 1e-3
	assert abs(soln.x()[0,1] - 0.5) < 1e-3
	assert abs(soln.x()[1,1] - 0.5) < 1e-3
	soln = reg_linear_least_squares(basis, y, 1e6, numpy.zeros((2,2)))
	print 'soln.x=', soln.x()
	assert abs(soln.x()[0,0]) < 1e-3
	assert abs(soln.x()[1,0]) < 1e-3
	assert abs(soln.x()[0,1]) < 1e-3
	assert abs(soln.x()[1,1]) < 1e-3
	soln = reg_linear_least_squares(basis, y, 1, [[0.5, 0.5],[0.5,0.5]], rscale=1e6)
	assert abs(soln.x()[0,0] - 0.5) < 1e-3
	assert abs(soln.x()[1,0] - 0.5) < 1e-3
	assert abs(soln.x()[0,1] - 0.5) < 1e-3
	assert abs(soln.x()[1,1] - 0.5) < 1e-3
	print 's', soln.x()
	print 'f', soln.fit()
	print 'r', soln.eff_rank()


def test_hat():
	"""Make sure that the hat function meets its definition."""
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y0 = numpy.transpose([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
	s0 = linear_least_squares(basis, y0)
	assert y0.shape[0] > 1
	for i in range(y0.shape[0]):
		y = numpy.array(y0)
		y[i] += 1
		s = linear_least_squares(basis, y)
		ishift = s.fit()[i] - s0.fit()[i]
		assert -0.001 <= ishift <= 1.001
		assert abs(ishift - s0.hat()[i]) < 0.001


if __name__ == '__main__':
	test0()
	test_svd()
	test_vec()
	test_m1()
	test_m2()
	test_vec2()
	test_m2r()
	test_m2rR()
	test_hat()
