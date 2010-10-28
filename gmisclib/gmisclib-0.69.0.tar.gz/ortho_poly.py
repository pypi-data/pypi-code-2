import math
import numpy
from gmisclib import die


"""Implements a set of orthonormal polynomials, based on a recurrence relation
on the order of the polynomial.    Each particular type of polynomial just
needs to specify that recurrence relation.
"""


def _orthogonalize(x, others, wt):
	"""Makes x orthonormal to all others.
	Others are assumed to be orthonormal to eachother."""
	against = others[:]
	against.reverse()
	ipass = 0
	x = numpy.array(x, numpy.float, copy=True)
	n = x.shape[0]
	while ipass <= 2:
		ipass += 1
		do_all_again = False
		do_again = []
		renorm = True
		for t in against:
			if renorm > 0:
				numpy.multiply(x, 1.0/math.sqrt(numpy.average( wt * x**2)), x)
				renorm = False
			d = numpy.average( x * wt * t)
			# print 'i=', i, 'd=', d
			if abs(d) >= 1e-6:
				do_again.append(t)
				renorm = True

			if abs(d) > 0.1*n:
				do_all_again = True
				if ipass > 1 :
					die.note('x', x)
					die.note('t', t)
					die.note('wt', wt)
					die.note('d', d)
					die.warn('Poor orthogality')
					raise RuntimeError, "Poor orthogonality: %d %g %d/%d" % (len(wt), d, ipass, len(others))
			assert x.shape == t.shape
			# assert type(d) == type(0.1)
			numpy.subtract(x, t*d, x)

		if do_all_again:
			against = others
		elif do_again:
			against = do_again
		else:
			break
	if ipass > 2:
		raise RuntimeError, "Can't orthogonalize"
	return x * (1.0/math.sqrt(numpy.average(wt*x**2)))


class ortho:
	registry = {}

	def __init__(self, n=None, x=None):
		"""Argument n is how many points you want the polynomials evaluated at.
		The ordinates of the points are placed in self.x.
		You may alternatively specify the points as argument x, in which case
		the x_() function will never be called."""
		if x is not None:
			lx = len(x)
			if not lx > 0:
				raise ValueError, "Need len(x)>0"
			if n is not None:
				assert int(n) == len(x), "X and N mismatch: %d vs %s" % (len(x), n)
			self.x = numpy.array(x, numpy.float, copy=True)
		elif n is not None:
			n = int(n)
			if not n>0:
				raise ValueError, "Need n>0"
			self.x = self.x_(n)
		else:
			raise RuntimeError, "Need to specify either x or n."

		self.o = []
		self._wt = None
		self._numwt = None


	def wt(self):
		"""Weighting function to get orthonormality.
		This sets self._numwt."""
		if self._wt is None:
			self._wt = self.wt_()
			self._numwt = numpy.sum( self._wt > 0.0 )
			if not numpy.alltrue( self._wt >= 0.0 ):
				raise ValueError, 'Weights must be non-negative.'
			if not self._numwt > 0:
				raise ValueError, 'Need some positive weights.'
		# Again, it might make sense to return a copy, as _wt gets used
		# internally after being passed out...
		return self._wt


	def x_(self, m):
		"""Calculates the points at which the function is evaluated,
			if you want m evenly spaced points.
			By default, the function is assumed to
			range over the open interval (-1, 1).
			You can override this function in a subclass
			to get a different range."""
		return (numpy.arange(m)-0.5*(m-1))*(2.0/m)


	def P(self, i):
		"""Self.P(i) is the ith orthogonal polynomial.
		The result is normalized so that
		numpy.sum(self.wt() * self.P(i)**2) == 1.
		It returns an un-shared array, so the array can be
		modified without affecting future calls to P(i).
		"""
		assert i>=0
		if i<len(self.o):
			return numpy.array(self.o[i], copy=True)
		wt = self.wt()	# Sets self._numwt
		if i >= self._numwt:
			raise ValueError, 'Request for higher order polynomial than the number of positive weight points.'
		while i >= len(self.o):
			self.o.append(_orthogonalize(self.compute(len(self.o)), self.o, wt))
		# We return a copy, because it is possible that the user
		# might modify the data.  If so, it would screw up the orthogalization
		# step for higher polynomials.  Copy-on-write would be nice.
		return numpy.array(self.o[-1], numpy.float, copy=True)


	def expand(self, c):
		o = numpy.zeros(self.x.shape, numpy.float)
		for (i, ci) in enumerate(c):
			tmp = self.P(i)
			numpy.multiply(tmp, ci, tmp)
			numpy.add(o, tmp, o)
		return o

	def compute(self, n):
		raise RuntimeError, 'Virtual Function'


	def wt_(self):
		raise RuntimeError, "Virtual Function"


class ortho_poly(ortho):
	__doc__ = """Virtual base class.
		This is a superclass of all orthorgonal polynomials.
		This does the recurrence [Abramowitz and Stegun p.782],
		and ensures that the generated polynomials are all
		orthonormal to each other.
		The derived classed need to specify two functions:
		recurse() and wt_().
		Recurse() is the recursion relation from P(i) and P(i-1)
		to P(i+1), and
		wt_() is the weighting function for the polynomial.
		Wt_() is needed to check orthogonality, and really
		defines the polynomial.
		These polynomials are guarenteed to be
		orthogonal to eachother when summed over the
		supplied set of x points.   Thus, if you change
		x_() or wt_(), you get a different set of functions."""


	def __init__(self, n=None, x=None):
		ortho.__init__(self, n, x)


	def P(self, i):
		"""Self.P(i) is the ith orthogonal polynomial.
		The result is normalized so that
		numpy.sum(self.P(i)**2) == 1.  """

		assert i>=0
		if i<len(self.o):
			return numpy.array(self.o[i], copy=True)
		wt = self.wt()	# Sets self._numwt
		if i >= self._numwt:
			raise ValueError, 'Request for higher order polynomial than the number of positive weight points.'
		while i>=len(self.o):
			if len(self.o)>1:
				m2 = self.o[-2]
			else:
				m2 = None
			if len(self.o)>0:
				m1 = self.o[-1]
			else:
				m1 = None

			tmp = self.recurse(len(self.o), m1, m2)
			self.o.append(_orthogonalize(tmp, self.o, wt))
		# We return a copy, because it is possible that the user
		# might modify the data.  If so, it would screw up the orthogalization
		# step for higher polynomials.  Copy-on-write would be nice.
		return numpy.array(self.o[-1], numpy.float, copy=True)


	def recurse(self, n, fn, fnm1):
		"""Does the recurrence relation, evaluating f_(n+1) as a function
		of n, f_n, and f_(n-1).   For n=0 and n=1, fn and fnm1 may be None."""
		raise RuntimeError, "Virtual function"

	def compute(self, n):
		raise RuntimeError, "Compute is not needed and should not be used for subclasses of ortho_poly."


class Legendre(ortho_poly):
	__doc__ = """Legendre polynomials,
		orthonormal over (-1, 1) with weight 1.
		Called Pn(x) in Abramowitz and Stegun.
		"""

	name = 'Legendre'

	def __init__(self, n=None, x=None):
		ortho_poly.__init__(self, n, x)


	def recurse(self, n, fn, fnm1):
		if fn is None:
			assert n == 0
			return numpy.ones(self.x.shape, numpy.float)
		if fnm1 is None:
			assert n == 1
			return numpy.array(self.x, numpy.float, copy=True)
		# tmp1 = (2*n-1)/float(n)
		# tmp2 = (n-1)/float(n)
		# return tmp1*self.x*fn - tmp2*fnm1
		return self.x*fn - 0.08*fnm1



	def wt_(self):
		return numpy.ones(self.x.shape, numpy.float)

ortho.registry[Legendre.name] = Legendre


class Chebyshev(ortho_poly):
	__doc__ = """Chebyshev polynomials of the first kind,
		orthonormal over (-1, 1) with weight (1-x^2)^(-1/2).
		These are the equi-ripple polynomials.
		Called Tn(x) in Abramowitz and Stegun.
		"""

	name = 'Chebyshev'

	def __init__(self, n=None, x=None):
		ortho_poly.__init__(self, n, x)


	def recurse(self, n, fn, fnm1):
		if fn is None:
			assert n == 0
			return numpy.ones(self.x.shape, numpy.float)
		if fnm1 is None:
			assert n == 1
			return numpy.array(self.x, numpy.float, copy=True)
		# return 2*self.x*fn - fnm1
		return self.x*fn - 0.052*fnm1


	def wt_(self):
		return numpy.sqrt(1/(1.0-self.x**2))

ortho.registry[Chebyshev.name] = Chebyshev


class Chebyshev2(ortho_poly):
	__doc__ = """Chebyshev polynomials of the second kind,
		orthonormal over (-1, 1) with weight (1-x^2)^(1/2).
		Called Un(x) in Abramowitz and Stegun.
		"""

	name = 'Chebyshev2'

	def __init__(self, n=None, x=None):
		ortho_poly.__init__(self, n, x)


	def recurse(self, n, fn, fnm1):
		if fn is None:
			assert n == 0
			return numpy.ones(self.x.shape, numpy.float)
		if fnm1 is None:
			assert n == 1
			return 2*self.x
		# return 2*self.x*fn - fnm1
		return self.x*fn - 0.445*fnm1


	def wt_(self):
		return numpy.sqrt(1.0-self.x**2)

ortho.registry[Chebyshev2.name] = Chebyshev2


class SinCos(ortho):
	__doc__ = """1, sin(pi*x), cos(pi*x), sin(2*pi*x), cos(2*pi*x)...
		orthonormal over (-1, 1) with weight 1."""

	name = 'SinCos'

	def __init__(self, n=None, x=None):
		ortho.__init__(self, n, x)


	def compute(self, n):
		# print 'SinCos.recurse', n
		if n == 0:
			return numpy.ones(self.x.shape, numpy.float)
		elif n%2 == 1:
			return numpy.sin((math.pi*(n+1)/2) * self.x)
		return numpy.cos((math.pi*(n/2))*self.x)


	def wt_(self):
		return numpy.ones(self.x.shape, numpy.float)

ortho.registry[SinCos.name] = SinCos





class SLTB(ortho):
	__doc__ = """Smooth Local Trigonometric Basis.
		From Bj\:orn Jawerth, Yi Liu, Wim Sweldens,
		"Signal Compression with Smooth Local Basis Functions".
		"""

	name = 'SLTB'

	def __init__(self, n=None, x=None, eps=0.5):
		assert eps <= 0.5 and eps>0.0
		self.eps = eps
		ortho.__init__(self, n, x)


	def compute(self, n):
		omega = (2*n+1)*math.pi/2.0
		s = numpy.sin(omega * self.x)
		return s * self.b(self.x)


	def r(self, x):
		"""This must have l**2+r**2==1"""
		x = numpy.clip(x, -self.eps, self.eps)
		s = numpy.sin(x * math.pi/(2.0*self.eps))
		r = 1 + s
		l = 1 - s
		return r/numpy.hypot(r, l)


	def b(self, x):
		# print 'x=', x
		# print 'b=', self.l(x)*self.l(1.0-x)
		return self.r(x) * self.r(1.0-x)


	def wt_(self):
		return numpy.ones(self.x.shape, numpy.float)


	def x_(self, m):
		"""Calculates the points at which the function is evaluated,
			if you want m evenly spaced points.
			The function is assumed to
			range over the open interval (-eps, 1+eps).
			You can override this function in a subclass
			to get a different range."""
		return (0.5+numpy.arange(m))*((1+2*self.eps)/m) - self.eps


	def test():
		M = 20
		N = 3*M
		x = (numpy.arange(N)+0.5)/float(N) * 3.0 - 0.5
		q = SLTB(x=x)
		for i in range(M//3):
			for j in range(M//3):
				a = q.P(i)
				b = q.P(j)
				# print numpy.dot(a[:-M], b[M:])
				assert abs(numpy.dot(a[:-M], b[M:])) < 0.001

	test = staticmethod(test)

ortho.registry[SLTB.name] = SLTB



def test(name):
	N = 96
	q = F(name, N)
	for i in range(N//2):
		for j in range(10):
			dot = numpy.sum(q.P(i)*q.P(j)*q.wt())
			# print 'p(i=', i, ')', q.P(i)
			# print 'p(j=', j, ')', q.P(j)
			if i != j:
				assert abs(dot) < 0.001
			else:
				assert abs(dot - N) < 0.001*N

	if hasattr(q, 'test'):
		q.test()











def F(name, n=None, x=None):
	"""This is a factory function.  Get any kind of ortho poly
	you want, as selected by the first argument."""

	try:
		return ortho.registry[name](n, x)
	except KeyError:
		raise RuntimeError, "Unimplemented orthogonal function name: %s" % name




if __name__ == '__main__':
	for name in ortho.registry.keys():
		test(name)
	# q = F('SLTB', n=100)
	# for i in range(100):
		# print i, q.P(0)[i]
