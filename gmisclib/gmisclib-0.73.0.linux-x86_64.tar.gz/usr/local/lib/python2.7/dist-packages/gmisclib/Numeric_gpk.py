
import numpy
import math
pylab = None


def add_overlap(a, astart, b, bstart):
	"""Add arrays a and b in the overlap region.
	Return (data, start).
	If a, b are time series, they are assumed to have the
	same sampling rate.
	Astart and Bstart apply to the zeroth index.
	All other indices are assumed to match start and length.
	"""
	start = max(astart, bstart)
	end = min(astart+a.shape[0], bstart+b.shape[0])

	out = a[start-astart:end-astart] + b[start-bstart:end-bstart]

	return (out, start)




# def asinh(x):
        # sign = numpy.sign(x)
	# return sign*numpy.log(sign*x + numpy.sqrt(x*x + 1))
asinh = numpy.arcsinh

# def acosh(x):
	# assert numpy.all(numpy.less_equal(x, 1))
	# return numpy.log(x - numpy.sqrt(x*x-1))
acosh = numpy.arccosh


def zero_pad_end(d, padfactor=1):
	if padfactor == 0:
		return numpy.array(d, copy=True)
	elif padfactor<=0:
		raise ValueError, 'pad factor <= 0'
	assert len(d.shape) == 1
	n = d.shape[0]
	npad = int(round(n*padfactor))
	return numpy.concatenate( (d, numpy.zeros((npad,),  numpy.double)) )


def Poisson(nbar):
	"""Return a Poisson random integer, whose distribution has
	a mean = nbar.
	"""
	import random
	assert nbar >= 0.0
	if nbar < 20.0:
		L = math.exp(-nbar)
		k = -1
		p = 1.0
		while p >= L:
			k += 1
			p *= random.random()
	else:
		lp = 0.0
		lL = -nbar
		k = 0
		chunk = min( int(round (1 + nbar + 3*math.sqrt(nbar) )), 10000)
		while lp >= lL:
			ptmp = numpy.log(numpy.random.uniform(0.0, 1.0, chunk) )
			lpp = numpy.add.accumulate(ptmp) + lp
			fsm = numpy.nonzero(numpy.less(lpp, lL))[0]
			if fsm.shape[0] != 0:
				k += fsm[0]
				break
			k += ptmp.shape[0]
			lp = lpp[-1]
	return k



def _test_Poisson():
	Nbar = 0.01
	N = int(round(1000/Nbar))
	s = 0
	for i in range(N):
		s += Poisson(Nbar)
	assert abs(s-N*Nbar) < 5*math.sqrt(N*Nbar)


	Nbar = 25.0
	N = 1000
	s = 0
	for i in range(N):
		s += Poisson(Nbar)
	assert abs(s-N*Nbar) < 5*math.sqrt(N*Nbar)



def bevel_concat(a, b, bevel=0, bevel_overlap=1.0, delay=0,
			ta=None, tb=None):
	"""Concatenate two time series.  Bevel the edges,
	and overlap them slightly.

	Bevel_overlap controls the fractional overlap of the two bevels,
	and delay specifies an extra delay for b.

	If ta and/or tb are specified, return a tuple of
	(concatenated_time_series, tma, tmb) where tma and tmb are the locations
	corresponding to ta and tb in the corresponding input arrays.
	"""
	assert bevel >= 0
	if bevel > 0:
		bev = (0.5 + numpy.arange(bevel))/float(bevel)
	else:
		bev = 1
	bc = numpy.array(b, copy=True)
	bev = (0.5 + numpy.arange(bevel))/float(bevel)
	ans = a.shape[0]-1
	bns = bc.shape[0]-1
	bos = a.shape[0] - int(round(bevel_overlap*bevel)) + delay
	boe = bos + bc.shape[0]
	o = numpy.zeros((boe,), numpy.double)
	o[:a.shape[0]] = a
	if bevel > 0:
		numpy.multiply(o[:bevel], bev, o[:bevel])
		numpy.multiply(o[ans:ans-bevel:-1], bev, o[ans:ans-bevel:-1])
		numpy.multiply(bc[:bevel], bev, bc[:bevel])
		numpy.multiply(bc[bns:bns-bevel:-1], bev, bc[bns:bns-bevel:-1])
	numpy.add(o[bos:boe], bc, o[bos:boe])
	if ta is not None or tb is not None:
		if tb is not None:
			tb += bos
		return (o, ta, tb)
	else:
		return o


def argmax(a):
	i = numpy.argmax(a, axis=None)
	o = []
	for n in reversed(a.shape):
		o.append( i % n )
		i = i//n
	o.reverse()
	return tuple(o)


def _test_argmax():
	x = numpy.array([1,2,3,4,3])
	assert argmax(x) == (3,)
	x = numpy.array([[1,2,3,4,3], [0,1,0,1,0]])
	assert x[argmax(x)] == 4
	x = numpy.array([[1,2,3,4,3], [0,1,0,5,0]])
	assert x[argmax(x)] == 5
	x = numpy.array([[1,2], [3,4], [5,6], [0,1],[0,5],[0,7]])
	assert x[argmax(x)] == 7
	x = numpy.zeros((5,4,3,3,1,2), numpy.double)
	x[2,1,0,1,0,1] = 100.0
	assert argmax(x) == (2,1,0,1,0,1)
	x[0,0,0,0,0,0] = 200.0
	assert argmax(x) == (0,0,0,0,0,0)
	x[4,3,2,2,0,1] = 300.0
	assert argmax(x) == (4,3,2,2,0,1)
	x[4,3,2,2,0,0] = 400.0
	assert argmax(x) == (4,3,2,2,0,0)
	x[4,3,2,0,0,0] = 500.0
	assert argmax(x) == (4,3,2,0,0,0)


def N_maximum(a):
	assert len(a.shape) == 1
	return a[numpy.argmax(a)].item()


def N_minimum(a):
	assert len(a.shape) == 1
	return a[numpy.argmin(a)].item()




def N_frac_rank(a, fr):
	assert 0 <= fr <= 1.0
	tmp = numpy.sort(a)
	n = tmp.shape[0]
	assert n > 0, "Zero-sized array: cannot compute rank."
	return tmp[int(round((n-1)*fr))].item()


def N_mean_ad(a):
	"""Mean absolute deviation.   For a multi-dimensional array,
	it takes the MAD along the first axis, so
	N_mean_ad(x)[0]==N_mean_ad(x[:,0]).
	"""
	ctr = numpy.median(a)
	diff = numpy.subtract(a, ctr)
	return numpy.sum(numpy.absolute(diff), axis=0)/(diff.shape[0]-1)


def _test_N_mean_ad():
	x = numpy.zeros((2,1), numpy.double)
	x[0,0] = 1
	x[1,0] = 0
	assert numpy.allclose(N_mean_ad(x), [1.0])
	x = numpy.zeros((5,7), numpy.double)
	x[0,0] = 1
	y = N_mean_ad(x)
	assert y.shape == (7,)
	assert numpy.allclose(y, [(1.0-0.0)/4.0, 0, 0, 0, 0, 0, 0])
	assert abs(N_mean_ad(x)[0]-N_mean_ad(x[:,0])) < 0.001


def median_across(list_of_vec):
	"""Returns an element-by-element median of a list of Numeric vectors."""
	assert len(list_of_vec[0].shape) == 1
	o = numpy.zeros(list_of_vec[0].shape, numpy.double)
	tmp = numpy.zeros((len(list_of_vec),), numpy.double)
	for t in list_of_vec:
		assert t.shape == o.shape
	for i in range(o.shape[0]):
		for (j, v) in enumerate(list_of_vec):
			tmp[j] = v[i]
		o[i] = numpy.median(tmp)
	return o


# Median along the first axis.
def N_median(a, axis=0):
	"""Returns an element-by-element median of a list of Numeric vectors."""
	if len(a.shape) ==  1:
		return numpy.median(a)
	assert len(a.shape) == 2
	if axis == 1:
		o = numpy.zeros((a.shape[0],), numpy.double)
		for i in range(o.shape[0]):
			o[i] = numpy.median(a[i])
	o = numpy.zeros((a.shape[1],), numpy.double)
	a = numpy.array(a)
	for i in range(o.shape[0]):
		o[i] = numpy.median(a[:,i])
	return o

def N_median_across(a):
	return N_median(a, axis=0)


variance = numpy.var
stdev = numpy.std
make_diag = numpy.diag


def set_diag(x, a):
	"""Set the diagonal of a matrix x to be the vector a.
	If a is shorter than the diagonal of x, just set the beginning."""

	assert len(a.shape) == 1
	assert len(x.shape) == 2
	n = a.shape[0]
	assert x.shape[0] >= n
	assert x.shape[1] >= n
	for i in range(n):
		x[i,i] = a[i]


# Take the median along the first coordinate of a 2-D matrix,
# so if m.shape=(2,4) then the output will have shape (4,)
def _test_N_median_across():
	x = numpy.zeros((3,2), numpy.double)
	x[0,0] = 1
	x[1,0] = 2
	x[2,0] = 3
	y = N_median(x, axis=0)
	# y = N_median_across(x)
	print 'median_across=', y
	assert numpy.allclose(y, [2.0, 0.0])


def limit(low, x, high):
	return numpy.clip(x, low, high)



def trimmed_mean_sigma_across(list_of_vec, weights, clip):
	import gpkavg
	"""Returns an element-by-element trimmed_mean of a list of Numeric vectors.
	For instance, the first component of the output vector is the trimmed mean
	of the first component of all of the input vectors.
	"""
	import gpkavg
	assert len(list_of_vec[0].shape) == 1
	om = numpy.zeros(list_of_vec[0].shape, numpy.double)
	osig = numpy.zeros(list_of_vec[0].shape, numpy.double)
	tmp = numpy.zeros((len(list_of_vec),), numpy.double)
	for t in list_of_vec:
		assert t.shape == om.shape
	for i in range(om.shape[0]):
		for (j, v) in enumerate(list_of_vec):
			tmp[j] = v[i]
		om[i], osig[i] = gpkavg.avg(tmp, weights, clip)
	return (om, osig)

def trimmed_mean_across(list_of_vec, weights, clip):
	return trimmed_mean_sigma_across(list_of_vec, weights, clip)[0]

def trimmed_stdev_across(list_of_vec, weights, clip):
	return trimmed_mean_sigma_across(list_of_vec, weights, clip)[1]


def vec_variance(x):
	"""Take a component-by-component variance of a list of vectors."""
	n = len(x)
	if n < 2:
		raise ValueError, "Cannot take variance unless len(x)>1"
	x0 = x[0]
	sh = x0.shape
	s = numpy.zeros(sh, numpy.double)
	ss = numpy.zeros(sh, numpy.double)
	for xi in x:
		assert xi.shape == sh
		tmp = xi - x0
		numpy.add(s, tmp, s)
		numpy.add(ss, numpy.square(tmp), ss)
	return numpy.maximum(ss-numpy.square(s)/n, 0.0)/(n-1)




def qform(vec, mat):
	"""A quadratic form: vec*mat*vec,
	or vecs*mat*transpose(vecs)"""
	if len(vec.shape) != 1 or len(mat.shape) != 2:
		raise ValueError, ': '.join(["Can't handle input",
					     "requires vector*matrix(vector)",
					     "shapes are %s and %s" % (
							vec.shape, mat.shape)
						])
	if mat.shape != (vec.shape[0], vec.shape[0]):
		raise ValueError, ': '.join([
					"Matrix must be square and match the length of vector",
					"shapes are %s and %s" % (vec.shape, mat.shape)
					])
	return numpy.dot(vec, numpy.dot(mat, vec))



def KolmogorovSmirnov(d1, d2, w1=None, w2=None):
	d1 = numpy.asarray(d1)
	d2 = numpy.asarray(d2)
	assert len(d1.shape) == 1, 'd1.shape=%s' % str(d1.shape)
	assert len(d2.shape) == 1, 'd2.shape=%s' % str(d2.shape)
	if w1 is None:
		w1 = numpy.ones(d1.shape, numpy.double)
	if w2 is None:
		w2 = numpy.ones(d2.shape, numpy.double)
	ws1 = numpy.sum(w1)
	ws2 = numpy.sum(w2)
	i1 = numpy.argsort(d1)
	i2 = numpy.argsort(d2)
	c1 = 0.0
	c2 = 0.0
	j1 = 0
	j2 = 0
	maxdiff = 0.0
	while True:
		if abs(c1-c2) > maxdiff:
			maxdiff = abs(c1 - c2)
		if j1 < i1.shape[0]-1 and j2<i2.shape[0]-1:
			if d1[i1[j1]] < d2[i2[j2]]:
				j1 += 1
				c1 += w1[i1[j1]]/ws1
			elif d1[i1[j1]] > d2[i2[j2]]:
				j2 += 1
				c2 += w2[i2[j2]]/ws2
			else:
				j1 += 1
				c1 += w1[i1[j1]]/ws1
				j2 += 1
				c2 += w2[i2[j2]]/ws2
		elif j1==i1.shape[0]-1 and j2==i2.shape[0]-1:
			break
		elif j1 < i1.shape[0]-1:
			j1 += 1
			c1 += w1[i1[j1]]/ws1
		else:
			j2 += 1
			c2 += w2[i2[j2]]/ws2
	return maxdiff


def _testKS():
	assert KolmogorovSmirnov([1, 2, 3.01, 3, 4, 5], [1, 2, 3.01, 3, 4, 5]) < 0.001
	assert abs( KolmogorovSmirnov([1, 2, 3.01, 3, 4, 5], [1, 2, 3, 4, 5, 6]) - 0.16667) < 0.001
	print KolmogorovSmirnov([1, 2, 3.01, 3, 4, 5], [1, 2, 3, 4, 5])




def interpN(a, t):
	"""Interpolate array a to floating point indices, t,
	via nearest-neighbor interpolation.
	Returns a Numeric array.
	"""
	ii = numpy.around(t)
	n = a.shape[0]
	if not numpy.alltrue((ii>=0) * (ii<=n-1)):
		raise IndexError, "Index out of range."
	iii = ii.astype(numpy.int)
	return numpy.take(a, iii, axis=0)



def interp(a, t):
	"""Interpolate to a specified time axis.
	This does a linear interpolation.
	A is a Numpy array, and t is an array of times.
	@return: interpolated values
	@rtype: numpy array.
	"""
	n = a.shape[0]
	nt = t.shape[0]
	las = len(a.shape)
	# print 'a=', a.shape, a
	if las == 1:
		# print 'a.shape=', a.shape
		a = numpy.transpose([a])
	m = a.shape[1]
	ii = numpy.around(t)
	assert ii.shape == t.shape

	# print 't=', t
	# print 'n=', n, 'ii=', ii
	if not numpy.alltrue((ii>=0) * (ii<=n-1)):
		idxmin = numpy.argmin(t)
		idxmax = numpy.argmax(t)
		raise IndexError, "Index out of range: min=%g[index=%d,int=%d] max=%g[index=%d,int=%d] vs. %d" % (t[idxmin], idxmin, ii[idxmin], t[idxmax], idxmax, ii[idxmax], n)

	nearestT = ii.astype(numpy.int)
	assert nearestT.shape == t.shape

	nearestA = numpy.take(a, nearestT, axis=0)
	assert nearestA.shape == (nt,m)
	deltaT = t - nearestT
	assert deltaT.shape == nearestT.shape
	isupport = numpy.where((deltaT>=0)*(nearestT<n-1)+(nearestT<=0), 1, -1) + nearestT
	assert isupport.shape == (nearestA.shape[0],)
	assert isupport.shape == nearestT.shape
	assert isupport.shape == deltaT.shape
	# print 'a=',a 
	# print 'isupport=', isupport
	support = numpy.take(a, isupport, axis=0)
	assert support.shape == (nt,m)
	if len(a.shape) > 1:
		assert nearestA.shape == (nt,m)
		deltaA = (deltaT/(isupport-nearestT))[:,numpy.newaxis] * (support-nearestA)
		assert deltaA.shape[1] == a.shape[1]
	else:
		deltaA = (deltaT/(isupport-nearestT)) * (support-nearestA)
	assert deltaA.shape == nearestA.shape
	rv = nearestA + deltaA
	if las == 1:
		return rv[:,0]
	return rv


def _test_interp1():
	a = numpy.array([[1.0], [2.0]])
	# a = numpy.array([1.0, 2.0], numpy.double)
	t = numpy.array([0.5])
	q = interp(a, t)
	assert q.shape == (1,1)
	assert numpy.sum(numpy.absolute(interp(a, t) - [1.5])) < 1e-3


def split_into_clumps(x, threshold, minsize=1):
	"""This reports when the signal is above the threshold.
	@param x: a signal
	@type x: L{numpy.ndarray}, one-dimensional.
	@param threshold: a threshold.
	@type threshold: float
	@returns: [(start, stop), ...] for each region ("clump") where C{x>threshold}.
	"""
	assert len(x.shape) == 1
	gt = numpy.greater(x, threshold)
	chg = gt[1:] - gt[:-1]
	nz = numpy.nonzero(chg)[0]
	rv = []
	if gt[0]:
		last = 0
	else:
		last = None
	for i in nz:
		if last is None:
			last = i+1
		else:
			if minsize > 0:
				rv.append( (last, i+1) )
			last = None
	if last is not None and gt.shape[0]>=last+minsize:
		rv.append( (last, gt.shape[0]) )
	return rv


def _test_split_into_clumps():
	tmp = split_into_clumps(numpy.array([0,0,0,1,0,0]), 0.5)
	assert tmp == [(3,4)]
	tmp = split_into_clumps(numpy.array([1,0,0]), 0.5)
	assert tmp == [(0,1)]
	tmp = split_into_clumps(numpy.array([0,0,0,1]), 0.5)
	assert tmp == [(3,4)]
	tmp = split_into_clumps(numpy.array([1]), 0.5)
	assert tmp == [(0,1)]
	tmp = split_into_clumps(numpy.array([0]), 0.5)
	assert tmp == []
	tmp = split_into_clumps(numpy.array([1]), 0.5, minsize=2)
	assert tmp == []
	tmp = split_into_clumps(numpy.array([0,0,0,1,1,0]), 0.5, minsize=2)
	assert tmp == [(3,5)]


BLOCK = 8192

def block_stdev(x):
	"""This is just a alternative implementation of
	the standard deviation of each channel, but it is designed
	in a block-wise fashion so the total memory usage is
	not large.
	"""
	m = (x.shape[0]+BLOCK-1)//BLOCK
	avg = numpy.zeros((m, x.shape[1],))
	sum2 = numpy.zeros((x.shape[1],))
	nn = numpy.zeros((m,))
	i = 0
	j = 0
	while i < x.shape[0]:
		n = min(BLOCK, x.shape[0]-i)
		tmp = numpy.sum(x[i:i+BLOCK], axis=0)/n
		avg[j,:] = tmp
		numpy.add(sum2, numpy.sum(numpy.square(x[i:i+BLOCK]-tmp), axis=0), sum2)
		nn[j] = n
		i += BLOCK
		j += 1
	assert j == m
	avgavg = numpy.sum(nn[:,numpy.newaxis]*avg, axis=0)/float(x.shape[0])
	for i in range(m):
		numpy.add(sum2, nn[i]*numpy.square(avg[i,:]-avgavg), sum2)
	return numpy.sqrt(sum2/float(x.shape[0]-1))


# def _test_block_stdev():
	# n = BLOCK//2
	# while n < 4*BLOCK:
		# x = numpy.zeros((n,2))
		# x[0,0] = 1.0
		# x[0,1] = 2.0
		# x[1,0] = -1.0
		# avg2 = 2.0/float(n)
		# a2 = math.sqrt(((2-avg2)**2+(n-1)*avg2**2)/float(n-1))
		# answer = [math.sqrt(2/float(n-1)), a2]
		# calc = avg_dev(x)
		# assert numpy.sum(numpy.absolute(numpy.log(calc/answer))) < 0.001
		# n = (n*3)//2 + 17


def convolve(x, kernel):
	"""This is basically like numpy.convolve(x, kernel, 1) except that it
	properly handles the case where the kernel is longer than the data.
	"""
	assert len(kernel.shape) == 1
	assert len(x.shape) == 1, "Have not tried multidimensional data yet."
	if x.shape[0] > kernel.shape[0]:
		return numpy.convolve(x, kernel, 1)
	n = kernel.shape[0] - x.shape[0] + 1
	z = numpy.zeros((n,))
	xx = numpy.concatenate((z, x, z), axis=0)
	return numpy.convolve(xx, kernel, 1)[n:n+x.shape[0]]


class EdgesTooWide(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)


def edge_window(n, eleft, eright, typeleft="linear", typeright="linear", norm=None):
	"""Creates a window which is basically flat, but tapers off on the left and
	right edges.  The widths of the tapers can be controlled, as can the shapes.
	@param n: the width of the window
	@type n: C{int}
	@param eleft: the width of the left taper (i.e. at zero index, in samples).
	@type eleft: C{int}
	@param eright: the width of the right taper (i.e. at index near C{n}, in samples).
	@type eright: C{int}
	@param typeleft: what kind of taper on the left? (Defaults to C{"linear"}).
	@type typeleft: C{'linear'} or C{'cos'}
	@param typeright: what kind of taper on the right?  (Defaults to C{"linear"}).
	@type typeright: C{'linear'} or C{'cos'}
	@param norm: How to normalize?  The default is L{None}, which means no normalization.
		Providing a number C{x} will normalize the window so that the average of the
		C{window**x}==1.
	@type norm: L{None} or C{float != 0}.
	"""
	assert int(n) >= 0
	if not (eleft <= n and eright <= n):
		raise EdgesTooWide, "n=%d, eleft=%d eright=%d" % (n, eleft, eright)
	o = numpy.ones((n,))
	if eleft > 0:
		frac = (numpy.arange(eleft)+0.5)/eleft
		if typeleft == "cos":
			frac = (1.0 - numpy.cos(frac*math.pi))/2.0
		o[:eleft] = frac
		del frac
	if eright > 0:
		frac = ((eright-numpy.arange(eright))-0.5)/eright
		if typeright == "cos":
			frac = (1.0 - numpy.cos(frac*math.pi))/2.0
		numpy.multiply(o[n-eright:], frac, o[n-eright:])
	if norm is not None:
		numpy.divide(o, numpy.average(o**norm)**(1.0/norm), o)
	return o



def edge_window_t(t, eleft, eright, typeleft="linear", typeright="linear", norm=None):
	"""Computes a window which is basically flat, but tapers off on the left and
	right edges.  The widths of the tapers can be controlled, as can the shapes.
	@param t: an array of time values.  They are required to be monotonically increasing,
		and assumed to be linearly spaced.
	@type t: C{numpy.ndarray}
	@param eleft: the width of the left taper (i.e. at zero index, in time units).
	@type eleft: C{float}
	@param eright: the width of the right taper (i.e. at index near C{n}, in time units).
	@type eright: C{float}
	@param typeleft: what kind of taper on the left? (Defaults to C{"linear"}).
	@type typeleft: C{'linear'} or C{'cos'}
	@param typeright: what kind of taper on the right?  (Defaults to C{"linear"}).
	@type typeright: C{'linear'} or C{'cos'}
	@param norm: How to normalize?  The default is L{None}, which means no normalization.
		Providing a number C{x} will normalize the window so that the average of the
		C{window**x}==1.
	@type norm: L{None} or C{float != 0}.
	"""
	if not len(t)>1:
		raise ValueError, "Time axis too short: len(t)=%d" % len(t)
	t0 = float(t[0])
	te = float(t[-1])
	assert te > t0, "t=%s" % str(t)
	w = te - t0
	assert w > 0.0
	if not ( eleft <= w and eright <= w):
		return EdgesTooWide, "eleft=%s eright=%s w=%s" % (eleft, eright, w)
	o = numpy.ones(t.shape)
	if eleft > 0:
		nedge = int(math.ceil((eleft/w)*t.shape[0]))
		wedge = (nedge+1)*eleft/float(nedge)
		tx = t0 - 0.5*wedge/(nedge+1)
		if typeleft == 'cos':
			f = (1.0 - numpy.cos((math.pi/wedge)*(t[:nedge]-tx)))/2.0
		else:
			f = (t[:nedge]-tx)/wedge
		o[:nedge] = f
		del f
	if eright > 0:
		nedge = int(math.ceil((eright/w)*t.shape[0]))
		wedge = (nedge+1)*eright/float(nedge)
		tx = te + 0.5*wedge/(nedge+1)
		y = o.shape[0] - nedge
		if typeright == 'cos':
			f = (1.0 - numpy.cos((math.pi/wedge)*(tx-t[y:])))/2.0
		else:
			f = (tx-t[y:])/wedge
		numpy.multiply(o[y:], f, o[y:])
	if norm is not None:
		numpy.divide(o, numpy.average(o**norm)**(1.0/norm), o)
	return o


def _test_ew():
	t = 1.0 + 0.1*numpy.arange(100)
	for i in range(0,60,4):
		e = 0.0 + 0.1*i
		w = edge_window_t(t, e, 1.432*e, typeright="cos")
		pylab.plot(t, w)
	pylab.show()


if __name__ == '__main__':
	_test_split_into_clumps()
	_test_argmax()
	_test_interp1()
	_test_Poisson()
	_test_N_mean_ad()
	_test_N_median_across()
	# _test_block_stdev()
	_test_split_into_clumps()
	import pylab
	_test_ew()
