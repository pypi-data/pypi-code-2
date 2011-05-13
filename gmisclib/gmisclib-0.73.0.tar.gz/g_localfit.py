"""Fit a linear transform to a bunch of tt
input/output vectors.

@note: If you compute Pearson's R^2 via 1-localfit()/err_before_fit(), you get the "unadjusted" R^2 value.
	There is also an "adjusted" R^2 value, which is
	Ra^2 = 1-(1-R^2)*(n-1)/(n-p-1) where n is the number of data and p is the number of adjustable
	parameters of the linear regression.
@note: When you are computing Pearson's r^2 by way of localfit()/err_before_fit() the two function calls
	I{MUST} have the same data and flags.  Specifically, C{constant} must be equal in both calls.
"""


import numpy
import warnings
from gmisclib import gpk_lsq
from gmisclib import gpk_rlsq

_Float = numpy.dtype('float')

def err_before_fit(data, minsv=None, minsvr=None, constant=True):
	"""How much variation did the data have before the fit?
	This is used to compare with the error after the fit, to
	allow a F-test or ANOVA.    Strictly speaking, we compute
	the mean-squared error about a constant.
	@return: Returns the per-coordinate sum-squared-error
		of the output coordinates.
	@rtype: C{numpy.ndarray}
	@param data: See L{pack}.
	@type data: See L{pack}.
	"""

	tmp = []
	for (ioc) in data:
		if len(ioc) == 2:
			ic, oc = ioc
			tmp.append( (numpy.zeros((0,), _Float), oc) )
		elif len(ioc) == 3:
			ic, oc, w = ioc
			w = float(w)
			assert w >= 0.0
			tmp.append( (numpy.zeros((0,), _Float), oc, w) )
	A, B, errs, sv, rank = localfit(tmp, minsv=minsv, minsvr=minsvr, constant=constant)
	return errs



def pack(data, constant=True):
	"""Prepare the data array and (optionally) weight the data.
	@param data: [(input_coordinates, output_coordinates), ...]
		or [(input_coordinates, output_coordinates, weight), ...].
		A list of (in,out) tuples corresponding to the
		independent and dependent parameters of the linear transform.
		Both C{in} and C{out} are one-dimensional
		numpy vectors.   They don't need to have
		the same length, though (obviously) all instances of "in"
		need to have the same length and all instances of "out"
		also need to match one another.
		If C{weight} is given, it must be a scalar.
	@type data: [(L{numpy.ndarray}, L{numpy.ndarray}), ...] or
		[(L{numpy.ndarray}, L{numpy.ndarray}, float), ...]
	"""
	nd = len(data)
	if not ( nd > 0):
		raise ValueError, "No data: cannot deduce dimensionality."
	ic, oc = data[0][:2]	# We ignore the weight, if any.
	m = len(oc)	#: The number of output coordinates (data).
	if not (m > 0):
		raise ValueError, "Output coordinates have zero dimension."
	n = len(ic)	#: The number of input coordinates (parameters).
	use_c = bool(constant) #: Should we add a constant term?
	if not (n+use_c > 0):
		warnings.warn("g_localfit: This is a zero-parameter model.")
	i = numpy.zeros((nd, n+use_c), _Float)
	o = numpy.zeros((nd, m), _Float)
	try:
		if use_c and len(data[0])==2:
			for (j, iow) in enumerate(data):
				ic, oc = iow
				o[j,:] = oc
				i[j,0] = 1.0
				i[j,1:] = ic
		elif use_c and len(data[0])==3:
			for (j, iow) in enumerate(data):
				ic, oc, w = iow
				i[j,0] = 1.0
				i[j,1:] = ic
				w = float(w)
				numpy.multiply(oc, w, o[j,1:])
		elif len(data[0])==2:
			for (j, iow) in enumerate(data):
				ic, oc = iow
				o[j,:] = oc
				i[j,:] = ic
		elif len(data[0])==3:
			for (j, iow) in enumerate(data):
				ic, oc, w = iow
				i[j,:] = ic
				w = float(w)
				numpy.multiply(oc, w, o[j,:])
	except ValueError, x:
		if len(iow) != len(data[0]):
			raise ValueError, "Data must either be uniformly weighted or not: see data[%d]" % j
		if len(oc) != o.shape[1]:
			raise ValueError, "Output data length must match: got %d on data[%d], expecting %d" % (len(oc), j, o.shape[1])
		if len(ic) != i.shape[1]-use_c:
			raise ValueError, "Input data length must match: got %d on data[%d], expecting %d" % (len(oc), j, i.shape[1]-use_c)
	except TypeError, x:
		if 'float' in str(x):
			raise TypeError, "Weight must be convertible to float in data[%d]: %s" % (j, x)
	return (i, o, m, n)




# This is used to compute the matrix of derivitives,
# which is then used to compute the step in mcmcSQ.py
def localfit(data, minsv=None, minsvr=None, constant=True):
	"""Does a linear fit to data via a singular value decomposition
	algorithm.
	It returns the matrix A and vector B such that
	C{A*input_coordinates+B} is the best fit to C{output_coordinates}.
	@param minsv: sets the minimum useable singular value;
	@type minsv: float or None
	@param minsvr: sets the minimum useable s.v. in terms of the largest s.v.
	@type minsvr: float or None
	@param constant: Do you want a constant built into the linear equations?
	@type constant: Boolean
	@rtype: (A, B, errs, sv, rank) where
		- A is a 2-D C{numpy.ndarray} matrix.
		- B is a 1-D C{numpy.ndarray} vector (if constant, else C{None}).
		- errs is a C{numpy.ndarray} vector, one value for each output coordinate.
			The length is the same as the C{out} vector (see L{pack}).
		- sv is a C{numpy.ndarray} vector.
			The length is the same as the C{in} vector (see L{pack}).
	@return: (A, B, errs, sv, rank) where
		- A is the matrix of coefficients
		- B is a vector of constants. (Or L{None})  One constant per component of the
			C{out} vector in L{pack}.
		- errs Each component gives the sum of squared residuals for the corresponding
			component of the C{out} vector.
		- sv are the singular values, sorted into decreasing order.
	@param data: list of tuples.   See L{pack}.
	@type data: See L{pack}.
	"""

	ii, oo, m, n = pack(data, constant=constant)
	del data	# Reclaim memory
	soln = gpk_lsq.linear_least_squares(ii, oo, minsv=minsv, minsvr=minsvr, copy=False)
	assert soln.q == m
	del ii # Free unneeded memory.
	del oo # Free unneeded memory.
	errs = numpy.sum( numpy.square(soln.residual()), axis=0 )
	sv = soln.sv()
	x = soln.x(copy=False)
	rank = soln.rank()
	assert sv.shape[0]>=rank and sv.shape[0]<=n+1, "sv.shape=%s rank=%d m=%d n=%d" % (str(sv.shape), rank, m, n)
	assert rank <= 1+n
	assert len(errs) == m
	assert x.ndim == 2
	if constant:
		return ( x[1:,:].transpose(), x[0,:],
			errs, numpy.sort(sv)[::-1], rank
			)
	return ( x.transpose(), None,
			errs, numpy.sort(sv)[::-1], rank
			)



def reg_localfit(data, regstr=0.0, regtgt=None, rscale=None, constant=True):
	"""Does a linear fit to data via a singular value decomposition
	algorithm.
	It returns the matrix A and vector B such that
	C{A*input_coordinates+B} is the best fit to C{output_coordinates}.
	@param constant: Do you want a constant built into the linear equations?
	@type constant: Boolean
	@return: (A, B, errs, sv, rank) where
		- A is a 2-D C{numpy.ndarray} matrix.
		- B is a 1-D C{numpy.ndarray} vector (if constant, else C{None}).
		- errs is a C{numpy.ndarray} vector, one value for each output coordinate.
			It gives the sum of squared residuals.
		- sv are the singular values, sorted into decreasing order.
	@param data: list of tuples.   See L{pack}.
	@type data: See L{pack}.
	"""

	ii, oo, m, n = pack(data, constant=constant)
	del data	# Reclaim memory
	soln = gpk_lsq.reg_linear_least_squares(ii, oo, regstr=regstr, regtgt=regtgt, rscale=rscale, copy=False)
	del ii # Free unneeded memory.
	del oo # Free unneeded memory.
	errs = numpy.sum( numpy.square(soln.residual()), axis=0 )
	sv = soln.sv_unreg()
	x = soln.x(copy=False)
	rank = soln.eff_rank()
	# print 'm=', m, 'errs=', errs.shape, errs
	assert len(errs) == m
	assert x.ndim == 2
	if constant:
		return ( x[1:,:].transpose(), x[0,:],
			errs, numpy.sort(sv)[::-1], rank
			)
	return ( x.transpose(), None,
			errs, numpy.sort(sv)[::-1], rank
			)

# This is used to compute the matrix of derivitives,
# which is then used to compute the step in mcmcSQ.py
def robust_localfit(data, minsv=None, minsvr=None, constant=True):
	"""Data is [ (input_coordinates, output_coordinates), ... ]
	Minsv sets the minimum useable singular value;
	minsvr sets the minimum useable s.v. in terms of the largest s.v..
	It returns the matrix A and vector B such that the best fit
	is A*input_coordinates+B in a tuple
	(A, B, errs, rank).
	errs is a vector, one value for each output coordinate.
	Rank is the minimum rank of the various fits.

	Warning! Not tested.
	"""

	ii, oo, m, n = pack(data, constant=constant)
	del data # Reclaim memory
	errs = []
	rank = None
	const = numpy.zeros((m,), _Float)
	coef = numpy.zeros((n,m), _Float)
	for j in range(m):
		assert oo.shape[1] == m
		soln = gpk_rlsq.robust_linear_fit(ii, oo[:,j], 1, minsv=minsv, minsvr=minsvr, copy=False)
		errs.append( numpy.sum( numpy.square(soln.residual()) ) )
		if rank is None or rank > soln.rank():
			rank = soln.rank()
		const[j] = soln.x()[0]
		coef[:,j] = soln.x()[1:]
	del ii # Free unneeded memory.
	del oo # Free unneeded memory.
	assert rank <= 1+n
	assert len(errs) == m
	return ( coef.transpose(), const, errs, rank)



def fit_giving_sigmas(data, minsv=None, minsvr=None, constant=True):
	"""Does a linear fit to data via a singular value decomposition
	algorithm.
	It returns the matrix A and vector B such that
	C{A*input_coordinates+B} is the best fit to C{output_coordinates}.
	@param minsv: sets the minimum useable singular value;
	@param minsvr: sets the minimum useable s.v. in terms of the largest s.v.
	@type minsv: float or None
	@type minsvr: float or None
	@param constant: Do you want a constant built into the linear equations?
	@type constant: Boolean
	@return: (A, B, sigmaA, sigmaB) where
		- A is a 2-D C{numpy.ndarray} matrix.
		- B is a 1-D C{numpy.ndarray} vector (if constant, else C{None}).
			)
	@param data: [(input_coordinates, output_coordinates), ...].
		A list of (in,out) tuples corresponding to the
		independent and dependent parameters of the linear transform.
		Both C{in} and C{out} are one-dimensional
		L{numpy vectors<numpy.ndarray>}.   They don't need to have
		the same length, though (obviously) all instances of "in"
		need to have the same length and all instances of "out"
		also need to match one another.
	@type data: [(L{numpy.ndarray}, L{numpy.ndarray}), ...]
	"""

	ii, oo, m, n = pack(data, constant=constant)
	del data	# Reclaim memory
	soln = gpk_lsq.linear_least_squares(ii, oo, minsv=minsv, minsvr=minsvr)
	del ii # Free unneeded memory.
	del oo # Free unneeded memory.
	x = soln.x()
	sigmas = numpy.sqrt(soln.x_variances())
	assert sigmas.shape == x.shape
	assert x.ndim == 2
	if constant:
		return ( x[1:,:].transpose(), x[0,:],
			 sigmas[1:,:].transpose(), sigmas[0,:]
			)
	return ( x.transpose(), None,
			sigmas.transpose(), None
			)


def leaktest():
	import RandomArray
	while 1:
		d = []
		for i in range(100):
			d.append( (RandomArray.standard_normal((30,)),
					RandomArray.standard_normal((1000,))))
		localfit(d)

def test0():
	d = [( numpy.zeros((0,)), numpy.array((1,)) ),
		( numpy.zeros((0,)), numpy.array((2,)) ),
		( numpy.zeros((0,)), numpy.array((3,)) )
		]
	coef, const, errs, sv, rank = localfit(d, constant=False)
	assert const is None
	assert coef.shape == (1,0)
	assert len(errs) == 1
	assert abs(errs[0]-14) < 1e-4
	assert rank==0
	assert abs(err_before_fit(d, constant=False)-errs[0]) < 1e-4


def test_localfit11(r):
	d = [	(numpy.array((0,)), numpy.array((-1,))),
		(numpy.array((1,)), numpy.array((0,))),
		(numpy.array((2,)), numpy.array((1+1e-7,))),
		(numpy.array((3,)), numpy.array((2,))),
		]
	if r:
		# INCOMPATIBILITY HERE!
		coef, const, errs, sv, rank = r_localfit(d)
	else:
		coef, const, errs, sv, rank = localfit(d)
	assert const.shape == (1,)
	assert abs(const[0]-(-1)) < 1e-6
	assert coef.shape == (1,1)
	assert abs(coef[0,0]-1) < 1e-6
	assert len(errs)==1
	assert errs[0] < 1e-6
	assert len(sv) == 2
	assert rank == 2
	assert numpy.alltrue(err_before_fit(d) >= errs)


def test_localfit11e():
	d = [	(numpy.array((0.0,)), numpy.array((0.0,))),
		(numpy.array((1.0,)), numpy.array((1.0,))),
		(numpy.array((2.0,)), numpy.array((0.0,))),
		(numpy.array((3.0,)), numpy.array((-2.0,))),
		(numpy.array((4.0,)), numpy.array((0.0,))),
		(numpy.array((5.0,)), numpy.array((1.0,))),
		(numpy.array((6.0,)), numpy.array((0.0,))),
		]
	coef, const, errs, sv, rank = localfit(d)
	print 'coef=', coef
	print 'const=', const
	print 'errs=', errs
	assert const.shape == (1,)
	assert abs(const[0]-0) < 1e-6
	assert coef.shape == (1,1)
	assert abs(coef[0,0]-0) < 1e-6
	assert len(errs)==1
	assert abs(errs[0]-6) < 1e-6
	assert len(sv) == 2
	assert rank == 2
	assert numpy.absolute(err_before_fit(d)-errs).sum() < 1e-6


def test_localfit21():
	d = [ (numpy.array((0,0)), numpy.array((-1,))),
		(numpy.array((1,2)), numpy.array((0,))),
		(numpy.array((2,-1)), numpy.array((1,))) ]
	coef, const, errs, sv, rank = localfit(d)
	assert const.shape == (1,)
	assert abs(const[0]-(-1)) < 1e-6
	assert coef.shape == (1,2)
	assert numpy.absolute(coef-[[1,0]]).sum() < 1e-6
	assert len(errs)==1
	assert errs[0] < 1e-6
	assert len(sv) == 3
	assert rank == 3
	assert numpy.alltrue(err_before_fit(d) >= errs)

def test_localfit21u():
	d = [ (numpy.array((0,0)), numpy.array((-1,))),
		(numpy.array((2,-1)), numpy.array((1,))) ]
	coef, const, errs, sv, rank = localfit(d)
	assert const.shape == (1,)
	assert abs(const[0]-(-1)) < 1e-6
	assert abs(const[0] + 2*coef[0,0]-coef[0,1] - 1) < 1e-6
	assert coef.shape == (1,2)
	assert len(errs)==1
	assert errs[0] < 1e-6
	assert len(sv) == 2
	assert rank == 2
	assert numpy.alltrue(err_before_fit(d) >= errs)


def test_localfit22(r):
	d = [ (numpy.array((0,0)), numpy.array((-1,0))),
		(numpy.array((1,2)), numpy.array((0,1.0))),
		(numpy.array((-1,2)), numpy.array((-2,1.0))),
		(numpy.array((-1,1)), numpy.array((-2+1e-7,0.5+1e-7))),
		(numpy.array((2,-1)), numpy.array((1,-0.5))) ]

	if r:
		coef, const, errs, sv, rank = r_localfit(d)
	else:
		coef, const, errs, sv, rank = localfit(d)

	print const
	print coef
	print  errs
	print  sv
	print rank
	assert const.shape == (2,)
	assert numpy.absolute(const - [-1,0]).sum() < 1e-6
	assert coef.shape == (2,2)
	assert numpy.absolute(coef[0]-[1,0]).sum() < 1e-6
	assert numpy.absolute(coef[1]-[0,0.5]).sum() < 1e-6
	assert len(errs)==2
	assert errs.sum() < 1e-6
	assert len(sv) == 3
	assert rank == 3
	assert numpy.alltrue(err_before_fit(d) >= errs)


def test_fgs1():
	N = 2000
	DSIG = 10.0
	import random
	import math
	d = []
	for i in range(N):
		s = random.normalvariate(0.0, DSIG)
		d.append((numpy.array([-1.0]), numpy.array([1-s])))
		d.append((numpy.array([1.0]), numpy.array([1+s])))
	coef, const, scoef, sconst = fit_giving_sigmas(d)
	assert abs(coef[0][0]) < 3*DSIG/math.sqrt(N)
	assert abs(coef[0][0]) > 0.001*DSIG/math.sqrt(N)
	assert abs(const[0]-1.0) < DSIG/math.sqrt(N)
	assert sconst[0] < DSIG/math.sqrt(N)
	assert abs(coef[0][0]) < 4*DSIG/2.0/math.sqrt(N)
	assert scoef[0][0] < 1.3*DSIG/math.sqrt(N)
	assert scoef[0][0] > 0.7*DSIG/math.sqrt(N)
	print 'FGS1 OK'


def test_wt():
	N = 1000
	DSIG = 1.0
	import random
	d = []
	for i in range(N):
		s = random.normalvariate(0.0, DSIG)
		x = random.normalvariate(0.0, DSIG)
		w = random.expovariate(1.0)
		d.append((numpy.array([-x]), numpy.array([1-s]), w))
		d.append((numpy.array([x]), numpy.array([1+s]), w))
		d.append((numpy.array([x]), numpy.array([1-s]), w))
		d.append((numpy.array([-x]), numpy.array([1+s]), w))
	var1 = err_before_fit(d)
	A, B, errs, sv, rank = localfit(d)
	assert numpy.absolute((var1-errs)).sum() < 0.1


if __name__ == '__main__':
	test0()
	test_wt()
	test_localfit11(False)
	test_localfit11e()
	test_localfit21()
	test_localfit21u()
	for r in [False]:	# Do Not test r_localfit()
		test_localfit11(r)
		test_localfit22(r)
	test_fgs1()
