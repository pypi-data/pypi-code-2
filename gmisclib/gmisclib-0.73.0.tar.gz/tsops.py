"""Do mathematical operations on time series, where
the two operands don't necessarily have the same
sampling times.     It finds a common sampling time
and sampling interval, then interpolates as necessary
to bring the data onto the common time axis.
"""

import math
from gmisclib import Num
from gmisclib import Numeric_gpk as NG
import gpkimgclass


class axis:
	"""This class represents a time axis for a time series.
	Indices of the underlying array are assumed to be zero-based.
	"""

	def __init__(self, start=None, dt=None, n=None, end=None, crpix=0):
		if start is not None and end is not None and n is not None:
			self.crval = start
			self.n = int(round(n))
			self.cdelt = (end-start)/float(n-1)
		elif start is not None and n is not None and dt is not None:
			self.crval = start
			self.n = n
			self.cdelt = dt
		elif start is not None and dt is not None and end is not None:
			self.crval = start
			self.n = 1 + abs(int(math.floor((end-start)/dt)))
			# print '# self.n = 1+round(', (end-start)/dt, ')=', self.n
			if end > start:
				self.cdelt = dt
			else:
				self.cdelt = -dt
		else:
			raise ValueError, "Either silly values or not implemented."
		assert self.n >= 0, "Silly number of data"
		self.crpix = crpix
		# print 'info=', self.crval, 'at', self.crpix, 'dt=', self.cdelt, 'n=', self.n
		assert round(self.index(self.start())) == 0, 'start fail: %s' % self
		assert round(self.index(self.end())) == self.n-1, 'end fail: %s' % self

	def N(self):
		return self.n

	def coord(self, index):
		"""What is the i^th coordinate if the i^th index==index?
		More plainly, this function gives you the coordinate that
		corresponds to the index."""
		assert self.n >= 0
		return self.crval + (index-self.crpix) * self.cdelt
	

	def coords(self):
		"""Generate an array of all the time values."""
		assert self.n >= 0
		index = Num.arrayrange(self.n)
		return index*self.cdelt + (self.crval-self.crpix*self.cdelt)


	def index(self, t, limit=False, error=True):
		assert self.n > 0
		assert self.cdelt != 0
		tmp = self.crpix + (t-self.crval)/self.cdelt
		if limit:
			rtmp = round(tmp)
			if not ( rtmp >= 0 ):
				tmp = 0.0
			elif not (rtmp < self.n):
				tmp = self.n - 1.0
		elif error and not 0 <= round(tmp) < self.n:
			raise IndexError, "coordinate out of range: %g->%.1f" % (t, tmp)
		return tmp


	def indices(self, t, limit=False, error=True):
		assert self.n > 0
		assert self.cdelt != 0
		tmp = self.crpix + (t-self.crval)/self.cdelt
		if limit:
			Num.maximum(tmp, 0.0, tmp)
			Num.minimum(tmp, self.n-1, tmp)
		elif error:
			nbad = Num.sum(Num.less(tmp, -0.5)) + Num.sum(Num.greater(tmp,self.n-0.5))
			if nbad:
				raise IndexError, "%d coordinates out of range" % nbad
		return tmp


	def dt(self):
		return self.cdelt


	def start(self):
		return self.coord(0)

	def end(self):
		return self.coord(self.n-1)

	def __str__(self):
		return '<axis start=%g end=%g dt=%g n=%d>' % (self.start(), self.end(),
								self.dt(), self.N()
								)
	__repr__ = __str__


def time(datasets, start=None, end=None):
	dts = 0.0
	dtn = 0
	for x in datasets:
		tdt = x.dt()
		dts += math.log(tdt)
		dtn += 1
	dt = math.exp(dts/dtn)

	_s = [x.start() for x in datasets ]
	if start is not None:
		_s.append(start)
	_start = max(_s)
	_e = [x.end() for x in datasets]
	if end is not None:
		_e.append(end)
	_end = min(_e)

	n = int(math.floor( ( _end - _start ) / dt ) )
	if n < 0:
		n = 0
	return axis( start=_start, dt=dt, n=n )


def time2(a, b):
	dt = 0.5*( a.dt() + b.dt() )
	start = max(a.start(), b.start())
	end0 = min(a.end(), b.end())
	n = int(math.floor((end0-start)/dt))
	return axis(start=start, dt=dt, n=n)


def _fill_interp_guts(a, t, fill, interpolator):
	"""Returns a Numeric array."""
	assert len(t.shape) == 1
	if a.n[2] == 0:
		# This case catches empty datasets.
		return Num.zeros((t.shape[0], a.n[1]), Num.Float) + fill
	noneedfill = Num.greater_equal(t, a.start()) * Num.less_equal(t, a.end())
	assert len(noneedfill.shape) == 1
	# print 'nnf', noneedfill
	nofillidx = Num.nonzero(noneedfill)[0]
	# print 'nfi', nofillidx
	if nofillidx.shape != t.shape:
		# print 't.shape=', t.shape
		ainofill = interpolator(a, Num.take(t, nofillidx, axis=0))
		# print 'ainf', ainofill
		out = Num.zeros((t.shape[0], a.n[1]), Num.Float) + fill
		# print 'out1=', out
		Num.put(out, nofillidx, ainofill)
		# print 'out2=', out
		# print 'outshape=', out.shape
	else:
		out = interpolator(a, t)
		# print 'Outshape=', out.shape
	return out


def test_fig():
	print "TEST_FIG"
	a = axis(start=2.0, dt=1.0, n=10)
	a.n = (0, 1, 10)
	t = Num.arrayrange(20)
	fill = -1
	ifcn = lambda a, b: 100
	q = _fill_interp_guts(a, t, fill, ifcn)
	print q
	print q.shape


def interp_fill(a, t, fill):
	return _fill_interp_guts(a, t, fill, interp)

def interpN_fill(a, t, fill):
	return _fill_interp_guts(a, t, fill, interpN)



def interp(a, t):
	"""Interpolate to a specified time axis.
	This does a linear interpolation.
	@param a: data to be interpolated (a time series)
	@type a: gpkimgclass.gpk_img
	@type t: an array of times.
	@rtype: numpy array.
	@return: data interpolated onto the specified time values.
	"""
	idx = a.t_index(t)
	return NG.interp(a.d, idx)



def test_interp1():
	x = Num.array([0, 1], Num.Float)
	xx = gpkimgclass.gpk_img({'CDELT2':1.0, 'CRPIX2':1, 'CRVAL2':0}, x)
	t = Num.array([0.0, 0.7, 0.99, 1.0], Num.Float)
	q = interp(xx, t)
	print q.shape, t.shape, x.shape, xx.d.shape
	print q
	assert q.shape[0] == t.shape[0]
	assert len(q.shape) == len(xx.d.shape)
	assert Num.sum(Num.absolute(q-[[0.0], [0.7], [0.99], [1.0]]))<1e-6
	qq = gpkimgclass.gpk_img({'CDELT2':1.0, 'CRPIX2':1, 'CRVAL2':0}, q)
	print 'qq.n', qq.n, xx.n
	assert qq.n[1] == xx.n[1] and qq.n[2] == t.shape[0]
	qn = interpN(xx, t)
	print 'qn=', qn
	assert Num.sum(Num.absolute(qn-[[0.0], [1.0], [1.0], [1.0]]))<1e-6

def test_interp2():
	x = Num.array([0, 1, 1.5], Num.Float)
	xx = gpkimgclass.gpk_img({'CDELT2':1.0, 'CRPIX2':1, 'CRVAL2':0}, x)
	t = Num.array([0.0, 0.7, 0.99, 1.0, 1.1, 2.0], Num.Float)
	q = interp(xx, t)
	assert Num.sum(Num.absolute(q-[[0.0], [0.7], [0.99], [1.0], [1.05], [1.5]]))<1e-6
	qn = interp(xx, t)
	assert Num.sum(Num.absolute(qn-[[0.0], [0.7], [0.99], [1.0], [1.05], [1.5]]))<1e-6


def test_interp3():
	x = Num.array([[0, 100], [1, 101], [1.5, 101.5]], Num.Float)
	xx = gpkimgclass.gpk_img({'CDELT2':1.0, 'CRPIX2':1, 'CRVAL2':0}, x)
	t = Num.array([0.0, 0.7, 0.99, 1.0, 1.1, 2.0], Num.Float)
	q = interp(xx, t)
	print q
	qq = gpkimgclass.gpk_img({'CDELT2':1.0, 'CRPIX2':1, 'CRVAL2':0}, q)
	print 'qq.n', qq.n, xx.n
	assert qq.n[1] == xx.n[1] and qq.n[2] == t.shape[0]
	assert Num.sum(Num.absolute(q-[[0.0, 100.0], [0.7, 100.7], [0.99, 100.99],
					[1.0, 101.0], [1.05, 101.05], [1.5, 101.5]]))<1e-6
	qn = interp(xx, t)
	assert Num.sum(Num.absolute(qn-[[0.0, 100.0], [0.7, 100.7], [0.99, 100.99],
					[1.0, 101.0], [1.05, 101.05], [1.5, 101.5]]))<1e-6



def interpN(a, t):
	"""Interpolate to a specified time axis via
	nearest-neighbor interpolation.
	A is a gpkimgclass, and t is an array of times.
	Returns a Numeric array, not a gpkimgclass.
	"""
	# print "interp.a=", a
	# print "interp.t=", t
	idx = a.t_index(t)
	return NG.interpN(a.d, idx)



def common(data_sets, start=None, end=None):
	"""Computes a common time axis for several datasets.
	Linearly interpolate as needed.
	The data sets need not be the same width, and need not have the
	same sampling interval or a common starting time.
	@param data_sets: this is a list of the data to be put on a common time axis.
	@type data_sets: L{list}(L{gpkimgclass.gpk_img})
	@param start: this allows you to restrict the output data to a smaller region.
	@param end: this allows you to restrict the output data to a smaller region.
	@type start: L{float} or L{None}
	@type end: L{float} or L{None}
	@rtype: list(numpy.ndarray) where the first ndarray is 1-D and the rest are two dimensional.
	@return: the time_axis (as a 1-D numpy array of time values),
		followed by a 2-D numpy array for each of the input data sets.
	"""
	tt = time(data_sets, start=start, end=end)
	t = tt.coords()

	return [tt] + [ interp(x, t) for x in data_sets ]



def commonN(data_sets, start=None, end=None):
	"""Put several data sets on a common time axis.
	Interpolate by choosing nearest neighbor.
	"""
	tt = time(data_sets, start=start, end=end)
	t = tt.coords()

	return [t] + [ interpN(x, t) for x in data_sets ]


def mul(a, b, hdr_op=None):
	tt = time((a, b))
	t = tt.coords()
	# print "t=", t
	ai = interp(a, t)
	bi = interp(b, t)
	# print "ai=", ai
	# print "bi=", bi
	c = ai * bi
	# print "c=", c

	if hdr_op is None:
		h = {}
	else:
		h = hdr_op(a.hdr, b.hdr)

	h['CDELT2'] = tt.dt()
	h['CRVAL2'] = tt.start()
	h['CRPIX2'] = 1
	
	return gpkimgclass.gpk_img(h, c)



def copy_interval(a, t0, t1, hdr_op=None, mode="rr"):
	"""This copies the part of the time-series in a
	where t0 < t < t1.
	'a' is a gpk_img object.
	"""

	if hdr_op is None:
		h = a.hdr.copy()
	else:
		h = hdr_op(a.hdr, t0, t1)
	i0 = a.t_index(t0)
	i1 = a.t_index(t1)
	if mode[0] == "r":
		i0 = int(round(i0))
	elif mode[0] == "w":
		i0 = int(math.floor(i0))
	elif mode[0] == "n":
		i0 = int(math.ceil(i0))
	if mode[1] == "r":
		i1 = int(round(i1))
	elif mode[1] == "w":
		i1 = int(math.floor(i1))
	elif mode[1] == "n":
		i1 = int(math.ceil(i1))

	d = Num.array(a.d[i0:i1,:], Num.Float, copy=True)
	h['CRVAL2'] = a.time(i0)
	h['CRPIX2'] = 1
	return gpkimgclass.gpk_img(h, d)


def apply(fcn, a, hdrfcn=lambda x:x):
	"""Apply a function, point-by-point to the data in a."""
	return gpkimgclass.gpk_img(hdrfcn(a.hdr), fcn(a.d))


def resample(a, dt):
	import samplerate
	ratio = a.dt()/dt
	d = samplerate.resample(a.d, ratio)
	assert len(d.shape)==len(a.d.shape)
	assert d.shape[1]==a.d.shape[1], "d.shape[0]: %d -> %d" % (a.d.shape[0], d.shape[0])
	assert abs(float(d.shape[0])/float(a.d.shape[0]) - ratio) < 0.1
	h = a.hdr.copy()
	h['CDELT2'] = dt
	return gpkimgclass.gpk_img(h, d)


def test():
	a = gpkimgclass.gpk_img({'CDELT2':1.0, 'CRPIX2':1, 'CRVAL2':0.0},
				Num.arrayrange(10))
	b = gpkimgclass.gpk_img({'CDELT2':0.5, 'CRPIX2':1, 'CRVAL2':0.4},
				Num.arrayrange(10)*0.5+0.4)
	# print 'a=', a.d
	# print 'b=', b.d
	# print 'b.time()', b.time()
	ab = mul(a, b)
	# print 'ab=', ab.d
	# print 'ab.time()=', ab.time()
	err = ab.d - Num.transpose([ab.time()])**2
	# print 'err=', err
	assert Num.sum(err**2) < 1e-5



if __name__ == '__main__':
	test_interp1()
	test_interp2()
	test_interp3()
	test()
