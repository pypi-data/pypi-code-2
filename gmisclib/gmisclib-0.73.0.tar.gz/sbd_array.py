
import string
import Num

inttype = type(1)


class sbd:
	def __init__(self, sz, bw, _data = None):
		"""Constructs a symmetric band-diagonal matrix of sz*sz, with
		a nonzero bandwidth of bw.
		bw==0 corresponds to a diagonal matrix."""
		self.n = sz
		if bw > sz:
			raise ValueError, 'Bandwidth too large for size'
		self.kd = bw
		self.ldab = self.kd+1
		if _data is None:
			self.d = Num.zeros((self.n, self.ldab), Num.Float)
		else:
			self.d = _data	# Not a public interface!
		self.shape = (sz, sz)


	def __copy__(self):
		"""Copy the data, not just the data description."""
		return sbd(self.n, self.kd, Num.array(self.d, copy=True))

	def __deepcopy(self, m):
		return self.__copy__()


	def __idx2(self, key):
		"""Converts from (x,y) external representation of the
		matrix storage to the index where it is actually
		stored internally."""
		if len(key) != 2 or type(key[0])!=inttype or type(key[1])!=inttype:
			raise TypeError, 'Need two integer indices'
		diagdist = abs(key[1] - key[0])
		minidx = min(key[1], key[0])
		if minidx < 0:
			raise IndexError, 'indices must be positive'
		if diagdist > self.kd:
			raise IndexError, 'out of band: %d/%d/(%d,%d)'%(diagdist, self.kd, self.d.shape[0], self.d.shape[1])
		return (minidx, diagdist)


	def __getitem__(self, key):
		"""Pulls an element of the array.  Key is a 2-tuple that specifies the
		'virtual' position in the array (i.e., as if the array were a full
		square matrix, rather than a band diagonal symmetric matrix."""
		try:
			k0, k1 = self.__idx2(key)
		except IndexError:
			return 0.0
		return self.d[k0, k1]

	def __setitem__(self, key, value):
		k0, k1 = self.__idx2(key)
		self.d[k0, k1] = value

	def increment(self, key, delta):
		"""Increment a single value
		(and its symmetric partner, if off the diagonal)."""
		k0, k1 = self.__idx2(key)
		self.d[k0,k1] = delta + self.d[k0, k1]

	def bd_increment(self, key, delta):
		"""Block diagonal increment."""
		assert len(delta.shape) == 2
		assert delta.shape[0]==delta.shape[1]
		n = delta.shape[0]
		for i in range(n):
			e = n - i
			s = key + i
			# print "i=", i, "n=", n, "s=", s, "e=", e
			# print "sd.shape=", self.d[s,:e].shape
			# print "d.shape=", delta[i,i:].shape
			wrk = self.d[s,:e]
			Num.add(wrk, delta[i,i:], wrk)

	def __str__(self):
		o = []
		o.append( "<sbdarray\n")
		for i in range(self.n):
			o.append('[')
			for j in range(self.n):
				o.append( repr(self.__getitem__((i, j))) )
			o.append(']\n')
		o.append('>')
		return string.join(o, ' ');

	def __repr__(self):
		return self.__str__()

	def __pow__(self, other):
		return sbd(self.n, self.kd, (self.d)**other)

	def __getslice__(self, i, j):
		"""This is copy semantics, not shared reference.
		"""
		if i<0 or j<0:
			raise IndexError, 'indices must be positive'
		high = min(j, self.n)
		low = min(i, j)
		if high == low:
			return None
		rv = Num.zeros((high-low, self.n), Num.Float)
		for r in range(low, high):
			e = min(r+self.kd+1, self.n)
			rv[r-low,r:e] = self.d[r, 0:e-r]
		for r in range(max(0, low-self.kd), high):
			# Clunky, but correct:
			e = min(r+self.kd+1, self.n)
			ee = min(e, high)-low
			q = max(low-r, 0)
			rv[q+r-low:ee,r] = self.d[r, q:ee-(r-low)]
		return rv


def symmetrize(matrix, direction):
	return matrix


class NoSolutionError(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)


def solve(a, b0):
	""" solves a*x = b, where a is class sbd:
	symmetric, positive definite, and band-diagonal.
	Note that this destroys the contents of a."""
	b = Num.asarray(b0, Num.Float)
	if len(b.shape) == 1:
		# b = Num.array((b,), Num.Float)
		b = Num.reshape(b, (1, b.shape[0]))
	# print "b.shape=", b.shape
	assert a.n == b.shape[1]
	import lapack_dpb
	# print "type(a.d)==", type(a.d)
	# print "a.d=", a.d
	# print "ravel(a.d)=", Num.ravel(a.d)
	# print "a.ldab=", a.ldab
	result = lapack_dpb.dpbsv('L', a.n, a.kd, b.shape[0], a.d,
					a.ldab, b, max(1, a.n), 0)
	# print "result=", result
	if result['info'] != 0:
		raise NoSolutionError, 'Linear system has no solution. Lapack_dpb.dpbsv info code=%d' % result['info']
	# print "b=", b
	return b
 

def multiply(a, x):
	"""Calculates a*x, where a is class sbd:
	symmetric, positive definite, and band-diagonal."""
	xx = Num.asarray(x, Num.Float)
	assert len(xx.shape) == 1
	assert a.n == xx.shape[0]
	import dblas
	y = Num.zeros(xx.shape, Num.Float)
	# print "type(a.d)==", type(a.d)
	# print "a.d=", a.d
	# print "ravel(a.d)=", Num.ravel(a.d)
	# print "a.ldab=", a.ldab
	result = dblas.dsbmv('L', a.n, a.kd,
				Num.ones((1,), Num.Float), a.d,
				a.ldab, xx, 1,
				Num.zeros((1,), Num.Float),
				y, 1)
	assert result == 0
	# print "result=", result
	# print "b=", b
	return y


def test1():
	x = sbd(100, 10)
	x[0,0] = 1
	assert x[0,0] == 1
	x[99,99] = 2
	assert x[99,99] == 2
	x[10,0] = 10
	assert x[10,0] == 10
	assert x[0,10] == 10
	try:
		x[12,1] = 2
	except IndexError:
		pass
	else:
		raise RuntimeError, "whoops"


def err(a, b):
	return Num.sum(Num.square(a-b))

def test2():
	x = sbd(6,2)
	b = Num.zeros((6,), Num.Float) + 10
	for i in range(6):
		x[i,i] = 2
	x[2,1] = 0.5
	# print "x=", x
	y = solve(x, b)
	y_t = Num.array(([5, 4, 4, 5, 5, 5],))
	# print "y=", y, "y_t=", y_t
	# print "x=", x
	assert err(y_t, y) < 1e-9


def testm():
	a = sbd(6, 2)
	a[4,3] = 1
	a[4,4] = 2
	a[5,3] = 3
	a[5,5] = -1
	x = Num.array((1, 0, 0, 0, 0, 0), Num.Float)
	print multiply(a, x)
	x = Num.array((0, 0, 0, 0, 1, 0), Num.Float)
	print multiply(a, x)
	x = Num.array((0, 0, 0, 0, 0, 1), Num.Float)
	print multiply(a, x)


def testa():
	x = sbd(6, 2)
	x[4,3] = 1
	x[4,4] = 2
	x[5,3] = 3
	x[5,5] = -1

	y = x[:]
	# print "y=", y
	assert y[4,3]==1
	assert y[4,4]==2
	assert y[5,3]==3
	assert y[4,5]==0
	assert y[3,4]==1
	assert y[3,3]==0
	assert y[4,5]==0
	assert y[5,5] == -1
	y = x[5:6]
	# print "y=", y
	assert y[0,5] == -1
	assert y[0,3] == 3
	assert y[0,4] == 0

def testbdi():
	x = sbd(6,2)
	y = Num.array([[1, 2], [2, 3]])
	x.bd_increment(1, y)
	assert x[1,1]==1
	assert x[2,2]==3
	assert x[2,1]==2
	assert x[1,2]==2
	assert x[0,0]==0
	assert x[3,3]==0
	assert x[3,2]==0
	z = Num.array([[-1, 0, 1], [0, 0, 0], [0, 0, 0]])
	x.bd_increment(0, z)
	assert x[0,0]==-1
	assert x[0, 2]==1
	assert x[1,1]==1
	assert x[1, 2]==2

if __name__ == '__main__':
	test1()
	test2()
	testa()
	testbdi()
	testm()
