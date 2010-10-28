"""Generic linear best fits."""

import types
from gmisclib import Num


def fit(idata, fitting_fcns, ff_info=None, wt=None):
	"""Fits  data to a linear combination of fitting_fcns.
	@rtype: tuple
	@return: The returned value is a tuple of:
		the coefficients of the optimal solution (as an array),
		the residual (a single float number),
		the rank of the fit (int),
		an array of the singular values,
		and the best fit to the data.
		The returned value follows Num.LA.linear_least_squares(),
		except that residual is always calculated and is a scalar.
	@type idata: an array of (vector, info).
	@type fitting_fcns: an array of functions.
	@param fitting_fcns: the basis functions for the linear regression.
		The fitting functions return vectors (which must match the data).
		Fitting functions are called as f(info, ff_info, len(vector)).
		Vectors may have different lengths, as long as the
		corresponding data and fit vectors agree.
	"""

	nd = len(idata)
	assert wt is None or len(wt) == nd
	w = [None] * nd

	# We concatenate the data vectors to do one big fit all at once.
	# d_idx keeps track of where each vector starts and ends.
	d_idx = Num.zeros((nd+1,), Num.Int)
	nd_total = 0
	for i in range(nd):
		assert len(idata[i]) == 2
		assert type(idata[i]) == types.TupleType
		d_idx[i] = nd_total		# Where does that dataset start?
		nd_total = nd_total + len(idata[i][0])
	d_idx[nd] = nd_total

	# Build the data array:
	data = Num.zeros((nd_total,), Num.Float)
	for i in range(nd):
		if wt is None:
			w[i] = Num.ones((len(idata[i][0]),), Num.Float)
		else:
			assert len(wt[i]) == len(idata[i][0])
			w[i] = Num.asarray(wt[i], Num.Float)
		assert len(idata[i][0]) == d_idx[i+1]-d_idx[i]
		data[d_idx[i] : d_idx[i+1]] = Num.asarray(idata[i][0],
								Num.Float) * w[i]

	# Build the array of basis functions:
	nff = len(fitting_fcns)
	base = Num.zeros((nd_total, nff), Num.Float)
	for i in range(nd):
		for j in range(nff):
			ff = fitting_fcns[j]
			zfit = Num.asarray(ff(idata[i][1], ff_info, d_idx[i+1]-d_idx[i]),
						Num.Float)
			assert len(zfit.shape)==1
			assert zfit.shape[0] == d_idx[i+1]-d_idx[i]
			base[d_idx[i]:d_idx[i+1], j] = zfit * w[i]

	rcond = 1e-5
	x, resid, rank, s = Num.LA.linear_least_squares(base, data, rcond)
	bfit = Num.matrixmultiply(base, x)
	resid = Num.sum(Num.square(bfit-data).ravel())

	bestfit = []
	# Chop the fit array back up to match the input vectors:
	for i in range(nd):
		bestfit.append(bfit[d_idx[i]:d_idx[i+1]]/w[i])

	return x, resid, rank, s, bestfit







def test():
	test1()
	test2()
	test3()
	test4()
	test5()
	test6()

def test1():
	x, resid, rank, s, f = fit([([0,1,2,3,4,5], None)], [lambda di, fi, l: range(l)], None)
	assert abs(x[0]-1)<0.0001
	assert resid < 0.001
	assert rank == 1

def test2():
	x, resid, rank, s, f = fit([([0,1,2,3], None), ([0,1,2,3,4], None)], [lambda di, fi, l: range(l)], None)
	assert abs(x[0]-1)<0.0001
	assert resid < 0.001
	assert rank == 1

def test3():
	x, resid, rank, s, f = fit([([0,1,2,3], None), ([0,2,4,6], None)], [lambda di, fi, l: range(l)])
	assert abs(x[0]-1.5)<0.0001
	assert rank == 1
	x, resid, rank, s, f = fit([([0,1,2,3], None), ([0,2,4,6], None)], [lambda di, fi, l: range(l)], wt=[[1,1,1,1],[1e-10,1e-10,1e-10,1e-10]])
	assert abs(x[0]-1)<0.0001
	assert rank == 1

def test4():
	x, resid, rank, s, f = fit([([0,1,2,3], None), ([1,2,3,4], None)], [lambda di, fi, l: range(l), lambda di, fi, l: [1]*l], None)
	assert abs(x[0]-1)<0.0001
	assert abs(x[1]-0.5)<0.0001
	assert rank == 2

def test5():
	x, resid, rank, s, f = fit([([1,2,3,4], None)], [lambda di, fi, l: range(l), lambda di, fi, l: [1]*l])
	assert abs(x[0]-1)<0.0001
	assert abs(x[1]-1)<0.0001
	assert resid < 0.001
	assert rank == 2
	assert abs(f[0][0]-1)<0.001
	assert abs(f[0][1]-2)<0.001

def test6():
	x, resid, rank, s, f = fit(
					[([1,2,3,4], None)],
					[lambda di, fi, l: range(l), lambda di, fi, l: [1]*l],
					wt=[[5,2,3,1e-10]]
				)
	assert abs(x[0]-1)<0.0001
	assert abs(x[1]-1)<0.0001
	assert resid < 0.001
	assert rank == 2





if __name__ == '__main__' :
	test()
	print "OK: passed tests"
