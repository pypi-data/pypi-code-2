"""Fit a plane to some data."""


import g_lin_fit
import Num


class Error(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)


class NoDataError(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)

def plane(data, wt=None):
	"""Fit a plane to some data.
	where the fitting function is
	f = c[0]*1 + c[1]*dep[0] + c[2]*dep[1] + ...
	where c is the array of coefficients.
	The length of c is equal to the number of dependent
	variables in each datum.
	@param data: [ (independent, dependent, dependent...), ...]
	@return: (c, opt, resid, rank, sv), where
		bestfit is the best fit to the data
		(i.e., the values of f),
		resid is the residual (a single float number),
		rank the rank of the fit (int),
		and sv is the array of the singular values.
	"""
	idata = [ ( [ t[0] for t in data ], None) ]
	n = len(data)
	if n <= 0:
		raise NoDataError('No Data')

	dims = len(data[0])
	for t in data:
		if len(t) != dims:
			raise ValueError('Data length mismatch')
	ffi = Num.zeros((n, dims), Num.Float)
	ffi[:, 0] = 1
	for i in range(1, dims):
		for j in range(n):
			ffi[j, i] = data[j][i]

	ff = [lambda info, ffin, nn, ii=i: ffin[:,ii] for i in range(dims) ]

	opt, resid, rank, sv, bestfit = g_lin_fit.fit(idata, ff, ffi, wt)
	return (opt, bestfit[0], resid, rank, sv)



def test():
	data = [ (1, 0), (2, 2), (3, 4), (4, 6) ]
	opt, bestfit, resid, rank, sv = plane(data)
	assert rank == 2
	assert abs(resid) < 1e-6
	for i in range(len(data)):
		assert abs(bestfit[i] - data[i][0]) < 1e-6
	assert abs(opt[0] - 1) < 1e-6 and abs(opt[1]-0.5) < 1e-6

if __name__ == '__main__':
	test()
