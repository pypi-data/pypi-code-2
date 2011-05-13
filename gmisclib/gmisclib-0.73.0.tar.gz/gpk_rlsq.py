import numpy

# import gpkavg
from gmisclib import gpk_lsq


class NotEnoughData(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)


_Float = numpy.dtype('float')

class w_linear_least_squares(gpk_lsq.linear_least_squares):
	"""This solves the set of linear equations a*x = y, with weights w.
	Normally, a.shape==(m,n) and y.shape==(m,q),
	and the returned x.shape==(n,q).
	where m is the number of constraints provided by the data,
	n is the number of parameters to use in a fit
	(equivalently, the number of basis functions),
	and q is the number of separate sets of equations
	that you are fitting.
	Then, x has shape (n,q) and the_fit has shape (m,q).
	Interpreting this as a linear regression, there are n
	parameters in the model, and m measurements.
	Q is the number of times you apply the model to a
	different data set; each on yields a different solution.

	This uses gpk_lsq.linear_least_squares as the underlying algorithm.
	@note: Y may be a 1-D matrix (a vector), in which case
		the fit is a vector.    This is the normal
		case where you are fitting one equation.
		If y is a 2-D matrix,
		each column (second index) in y is a separate fit, and
		each column in the solution is a separate result.
	"""
	def __init__(self, a, y, w, minsv=None, minsvr=None, copy=True):
		a = numpy.asarray(a, _Float)
		if a.ndim != 2:
			raise ValueError, "a needs to be 2-dimensional: shape=%s" % str(a.shape)

		self.w = numpy.array(w, _Float, copy=copy)
		if self.w.ndim != 1 and self.w.shape[0] != a.shape[0]:
			raise ValueError, "w needs to be 1-dimensional and match a: shape=%s vs %s" % (str(self.w.shape), str(a.shape))

		aw = self.w[:,numpy.newaxis] * a
		gpk_lsq.linear_least_squares.__init__(self, aw, None, minsv=minsv,
								minsvr=minsvr, copy=False)
		self.set_y(y, copy=copy)


	def fit(self, copy=False):
		"""
		@note: all elements of C{w} must be nonzero.
		"""
		f = gpk_lsq.linear_least_squares.fit(self, copy=False)/self.w
		return f

	def y(self, copy=True):
		y = gpk_lsq.linear_least_squares.y(self, copy=False)/self.w
		return y

	def set_y(self, y, copy=True):
		if y is not None:
			y = self.w * y
		gpk_lsq.linear_least_squares.set_y(self, y, copy=False)
		

	def residual(self):
		r = self.y(copy=False) - self.fit(copy=False)
		return r




# class robust_linear_fit(lls_base):
class robust_linear_fit(w_linear_least_squares):
	HTMIN = 3.0
	STMIN = 1.5

	def __init__(self, a, y, sigma_y=None, minsv=None, minsvr=None, copy=True):
		"""This does bounded influence regression, with
		a robust M-estimator in the y-direction.
		"""

		y = numpy.array(y, _Float, copy=copy)
		assert y.ndim == 1
		ndat = y.shape[0]
		if sigma_y is None:
			sigma_y = 1.0
		if isinstance(sigma_y, (float, int)):
			self.sigma_y = sigma_y * numpy.ones(y.shape, _Float)
		else:
			self.sigma_y = numpy.asarray(sigma_y, _Float)
			assert self.sigma_y.ndim == 1
			assert self.sigma_y.shape[0] == ndat

		a = numpy.asarray(a, _Float)
		assert a.ndim == 2
		assert a.shape[0] == ndat
		
		if a.shape[1] >= ndat:
			raise NotEnoughData, "Not enough data to bound influence function"

		w = 0.0
		w_hat = numpy.ones(y.shape, _Float)
		w_resid = numpy.ones(y.shape, _Float)
		hthresh = 6*self.HTMIN
		sthresh = 6*self.STMIN
		endgame = False
		while True:
			last_w = w
			w = w_hat * w_resid
			if numpy.alltrue( numpy.absolute(w-last_w) < 0.01 ):
				if endgame:
					break
				else:
					hthresh = self.HTMIN
					sthresh = self.STMIN
					endgame = True
					# print 'ENDGAME'

			# print 'w=', w
			# print 'y=', y

			self.w = w
			wsig = w/self.sigma_y

			w_linear_least_squares.__init__(self, a, y, wsig, minsv=minsv, minsvr=minsvr)

			ht = (1 - 2.0/y.shape[0])/hthresh
			# print 'hat=', self.hat()
			if numpy.sometrue(self.hat() >= 1.0):
				raise NotEnoughData, "Cannot bound influence of point(s)."
			hatfac = (1-self.hat())/ht
			# print 'hatfac=', hatfac
			w_hat = numpy.minimum(1.0, w_hat*hatfac**0.5)
			# Keep largest weight at unity:
			w_hat = w_hat/w_hat[numpy.argmax(w_hat)]
			# print 'w_hat=', w_hat

			normerr = (y - self.fit())/self.sigma_y
			# print 'normerr=', normerr
			# self.typdev = gpkavg.avg(numpy.absolute(normerr), None, 0.25)[0]
			self.typdev = numpy.mean(numpy.absolute(normerr))
			new_w_resid = 1.0/numpy.hypot(1, normerr/(self.typdev * sthresh))
			w_resid = 0.5*(w_resid + new_w_resid)
			wrs = numpy.sqrt( numpy.square(w_resid).sum(axis=0)/ndat )
			numpy.divide(w_resid, wrs, w_resid)
			# print 'w_resid=', w_resid

			hthresh = self.HTMIN + 0.5*(hthresh-self.HTMIN)
			sthresh = self.STMIN + 0.5*(sthresh-self.STMIN)
			# print 'ht, st=', hthresh, sthresh
		# print "END"



def test_w1():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.array([0.0, 1, 2, 3, 4, 5, 6, 7, 18.01, 99])
	w = numpy.array([1, 3.2, 1, 1, 5, 1, 1, 1, .0001, 1])
	soln = w_linear_least_squares(basis, y, w)
	print 'soln.y', soln.y()
	assert (numpy.absolute(soln.y()-y)).sum() < 0.0001
	print 'soln.x', soln.x()
	print 'soln.fit', soln.fit()
	assert 80 < numpy.absolute(soln.fit()).sum() < 200
	assert soln.x().ndim == 1
	assert soln.fit().ndim == 1
	assert soln.rank() == 2
	print 'residual=', soln.residual()
	assert (numpy.absolute(soln.residual()) > 0.2).sum() == 1
	assert (numpy.absolute(soln.residual()) > 10.2).sum() == 0
	assert 0.5 < numpy.absolute(soln.residual()).sum() < 30
	err = ((soln.fit()-y)**2).sum()
	assert err>=0
	assert (err > 0.02).sum() == 1
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0] - 1) < 0.01
	assert abs(soln.x()[1] + 1) < 0.01
	assert numpy.absolute(w-soln.w).sum() < 1e-6
	assert numpy.absolute(numpy.dot(basis, soln.x())-soln.fit()).sum() < 1e-6



def test_w1b():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.array([0.01, 1, 2.01, 3, 3.99, 5, 6.01, 7, 88.01, 99])
	w = numpy.array([0.2, 1, 0.2, 5, 1, 0.2, 1, 2, .001, 0.01])
	soln = w_linear_least_squares(basis, y, w)
	print 'soln.x', soln.x()
	print 'soln.resid', soln.residual()
	assert (numpy.absolute(soln.residual()) > 0.05).sum() == 1
	assert abs(soln.x()[0] - 1) < 0.01
	assert abs(soln.x()[1] + 1) < 0.01
	print 'sf', soln.fit()
	print 'mm', numpy.dot(basis, soln.x())
	assert numpy.absolute(numpy.dot(basis, soln.x()) -soln.fit()).sum() < 1e-6

def test_r1():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.array([0.01, 1, 1.99, 3, 4.01, 5, 5.99, 7, 88.01, 99])
	soln = robust_linear_fit(basis, y, 1)
	print 'soln.x', soln.x()
	assert soln.x().ndim == 1
	assert soln.fit().ndim == 1
	assert soln.rank() == 2
	err = ((soln.fit()-y)**2).sum()
	assert err>=0
	assert (err > 0.02).sum() == 1
	assert soln.sv().shape == (2,)
	assert abs(soln.x()[0] - 1) < 0.06
	assert abs(soln.x()[1] + 1) < 0.06
	assert numpy.absolute(numpy.dot(basis, soln.x())
						-soln.fit()).sum() < 1e-5

def test_r1hat():
	basis = numpy.transpose([[1, 2, 3, 4, 5, 6, 7, 8, 9, 100],
				[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])
	y = numpy.array([0.01, 1, 1.99, 3, 4.01, 5, 5.99, 7, 8, 90])
	soln = robust_linear_fit(basis, y, 1)
	print 'soln.x', soln.x()
	assert soln.rank() == 2
	print 'resid=', soln.residual()
	assert (numpy.absolute(soln.residual()) > 0.4).sum() == 1
	assert abs(soln.x()[0] - 1) < 0.07
	assert abs(soln.x()[1] + 1) < 0.5
	assert numpy.absolute(numpy.dot(basis, soln.x())
						- soln.fit()).sum() < 1e-5


if __name__ == '__main__':
	test_w1()
	test_w1b()
	test_r1()
	test_r1hat()
