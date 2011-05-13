from __future__ import with_statement
import os
import sys
import math
import time
import stat
import errno

import die

try:
	from Numeric_gpk import N_maximum, N_minimum, N_median, N_mean_ad,	\
			variance, stdev,	\
			set_diag,	\
			make_diag, limit, vec_variance, qform,	\
			KolmogorovSmirnov, interp, interpN
except ImportError, _x:
	if str(_x).startswith('cannot import name'):
		raise
	pass


def median(x):
	"""
	@except ValueError: if the input list is zero length.
	"""
	xx = sorted(x)
	n = len(xx)
	if not (n > 0):
		raise ValueError, "No data to median."
	return 0.5*(xx[n//2] + xx[(n-1)//2])


def median_across(xl):
	"""
	@note: There is a version of this in Numeric_gpk that is more efficient when the input
		is a list of numpy.ndarray vectors.
	@except ValueError: If the input vectors are different lengths.
	@except ValueError: see L{median}.
	"""
	rv = []
	tl = None
	for (i, tup) in enumerate(zip(*xl)):
		if tl is None:
			tl = len(tup)
		elif tl != len(tup):
			raise ValueError, "Vector %d has a different length(%d) from the rest(%d)" % (i, len(tup), tl)
		rv.append(median(tup))
	return rv


def avg(x):
	s = 0.0
	n = 0
	for t in x:
		s += t
		n += 1
	return s/float(n)


def median_ad(x):
	"""Median absolute deviation"""
	medn = median(x)
	return median( [ abs(t-medn) for t in x ] )
mad = median_ad


def mean_ad(x):
	medn = median(x)
	sum = 0.0
	for t in x:
		sum += abs(t-medn)
	return (medn, sum/float(len(x)))


def geo_mean(*d):
	"""
	@except ValueError: if any argument is negative.
	@return: Geometric mean of its arguments.
	@rtype: float
	"""
	s = 0.0
	for t in d:
		if t == 0.0:
			return 0.0
		elif t > 0.0:
			s += math.log(t)
		else:
			raise ValueError, "Negative/NaN argument to geo_mean: %s" % str(t)
	return math.exp(s/len(d))



def entropy(x):
	"""Compute the entropy of a list of probabilities."""
	e = 0.0
	ps = 0.0
	for p in x:
		assert p <= 1.0
		if p > 0.0:
			e -= p*math.log(p)
		ps += p
	assert 0.999 < ps < 1.001, "Probabilities must sum to one."
	return e


def resample(d):
	"""Bootstrap resampling.  Call this many times: each one
	returns a random resampling.
	"""
	import random
	o = []
	for i in range(len(d)):
		o.append( random.choice(d) )
	return o


def jackknife(d):
	"""Jackknife resampling.  Call this once.
	It returns a list of deleted lists."""
	for drop in range(len(d)):
		yield [ di for (i, di) in enumerate(d) if i!=drop ]






def Student_t_dens(x, n):
	"""From p.337 Statistical Theory by Bernard Lindgren."""

	from transcendental import gamma
	# http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/python/statistics.html	
	p = gamma((n+1)/2.0) * (1+x*x/n)**(-(n+1)/2.0) / (
			math.sqrt(n*math.pi)*gamma(n/2.0)
			)
	return p


def log_Student_t_dens(x, n):
	"""From p.337 Statistical Theory by Bernard Lindgren."""
	assert n > 0
	from gmisclib import stats
	# http://bonsai.ims.u-tokyo.ac.jp/~mdehoon/software/python/statistics.html	
	# p = gamma((n+1)/2.0) * (1+x*x/n)**(-(n+1)/2.0) / (
			# math.sqrt(n*math.pi)*gamma(n/2.0)
			# )
	lp = math.log(1+x*x/n)*(-(n+1)/2.0)
	lp += stats.gammaln((n+1)/2.0) - stats.gammaln(n/2.0)
	lp -= 0.5*math.log(n*math.pi)
	return lp




_fcache = {}
def log_factorial(n):
	assert n >= 0
	try:
		lf = _fcache[n]
	except KeyError:
		lf = 0.0
		for i in range(2,n):
			lf += math.log(i)
		_fcache[n] = lf
	return lf


def log_Combinations(n, m):
	assert n >= m
	assert m >= 0
	return log_factorial(n) - log_factorial(m) - log_factorial(n-m)

def ComplexMedian(P):
	"""P is a list of complex numbers.
	This algorithm works by repeatedly stripping off the convex
	hull of the points.
	"""
	import convex_hull2d
	import cmath
	import dictops
	HUGE = 1e30
	EPS = 1e-7
	Q = dictops.dict_of_accums()
	for p in P:
		Q.add(p, 1.0)

	while len(Q) > 3:
		# print 'Q=', Q
		edge = convex_hull2d.convexHull(Q.keys())
		# print 'edge=', edge
		ee = (edge[-1],) + edge + (edge[0],)
		wt = {}
		for i in range(1,len(edge)+1):
			em = ee[i] - ee[i-1]
			ep = ee[i+1] - ee[i]
			# angle = cmath.log(em).imag - cmath.log(ep).imag
			if min(abs(ep), abs(em)) < EPS*max(abs(em), abs(ep)):
				angle = math.pi/2.0	#Kluge, mild.   Roundoff errors.
			else:
				angle = cmath.log(em/ep).imag
			# KLUGE AND ROUNDOFF WARNING!
			if angle <= 0.0 and angle > -0.5:
				angle = EPS	#KLUGE!  Awful!
			if angle < 0.0:
				angle += 2*math.pi
			if angle >= math.pi and angle<math.pi+0.5:
				angle = math.pi-EPS	# KLUGE!  Awful!
			# print 'angle=', angle, ee[i-1], ee[i], ee[i+1], 'pi=', math.pi
			assert angle>=0 and angle<=math.pi, "angle=%g" % angle
			wt[ee[i]] = angle
		fmin = HUGE
		for p in edge:
			f = Q[p]/wt[p]
			if f < fmin:
				fmin = f
		# print 'fmin=', fmin
		assert fmin > 0.0
		sum = complex()
		swt = 0.0
		for p in edge:
			fwp = fmin * wt[p]
			# print 'Subtracting wt of ', fwp, 'from Q[', p, ']=', Q[p]
			swt  += fwp
			sum += p * fwp
			if Q[p] > fwp+EPS:
				Q[p] -= fwp
				# print '\tQ[', p, ']=', Q[p]
			else:	# Q[p]<=fwp
				assert abs(Q[p]-fwp) < EPS
				# print 'Deleting Q[', p, ']=', Q[p]
				del Q[p]
		if len(Q) == 0:
			return sum/swt
	# print 'Qfinal=', Q
	sum = complex()
	w = 0.0
	for (p,n) in Q.items():
		sum += p*n
		w += n
	return sum/w



def testCM():
	def eq(a, b):
		tmp = abs(a-b)/(abs(a)+abs(b)) < 1e-6
		if not tmp:
			print 'eq fails: %s vs %s' % (str(a), str(b))
		return tmp
	print 'CM'
	assert eq(ComplexMedian([complex(1,0), complex(2,0), complex(3,0)]), 2)
	assert eq(ComplexMedian([complex(1), complex(2), complex(3), complex(4)]), 2.5)
	assert eq(ComplexMedian([complex(1), complex(2), complex(3), complex(4), complex(5)]), 3)
	assert eq(ComplexMedian([complex(1), complex(2), complex(3), complex(4), complex(4)]), 3)
	assert eq(ComplexMedian([complex(1,1), complex(2,2), complex(3,3), complex(4,4)]),
			complex(2.5,2.5))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1), complex(1,1)]),
			complex(0.5,0.5))
	assert eq( ComplexMedian([complex(0,0), complex(1,0), complex(0,1),
				complex(1,1), complex(1,1)]),
			complex(1,1))
	assert eq( ComplexMedian([complex(0,0), complex(1,0), complex(0,1),
				complex(1,1), complex(0.6,0.6)]),
			complex(0.6,0.6))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1), complex(1,1),
				complex(0,0), complex(2,0), complex(0,2), complex(2,2)]),
			complex(0.5,0.5))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1)]),
			complex(1./3., 1./3.))
	assert eq(ComplexMedian([complex(0,0), complex(1,0), complex(0,1),
				complex(0,0), complex(2,0), complex(0,2)]),
			complex(0.3, 0.3))
	import cmath
	for N in [3, 4, 5, 6, 7, 8, 13, 40, 100, 2351]:
		print 'N=', N
		assert eq(ComplexMedian( [ 1+cmath.exp(2*cmath.pi*1j*float(q)/N)
						for q in range(N) ]),
				complex(1.0, 0.0)
				)





import Queue
import threading
class threaded_readable_file(object):
	QSIZE = 100
	_string = type('')

	def __init__(self, fd):
		self.q = Queue.Queue(self.QSIZE)

		def rhelper(fd, q):
			try:
				for l in fd:
					q.put(l)
				q.put(None)
				# while True:
					# l = fd.readline()
					# if l == '':
						# q.put(None)
						# break
					# else:
						# q.put(l)
						
			except (Exception, KeyboardInterrupt):
				q.put( sys.exc_info() )
	
		self.rh = threading.Thread(target=rhelper, args=(fd, self.q))
		self.rh.start()


	def readline(self):
		if self.q is None:
			return ''
		x = self.q.get()
		if type(x) != self._string:
			self.rh.join()
			self.q = None
			if x is not None:
				raise x[0], x[1], x[2]
			return ''
		return x


	def readlines(self):
		o = []
		while self.q is not None:
			x = self.q.get()
			if type(x) != self._string:
				self.rh.join()
				self.q = None
				if x is not None:
					raise x[0], x[1], x[2]
				break
			o.append( x )
		return o


	def read_iter(self):
		while self.q is not None:
			x = self.q.get()
			if type(x) != self._string:
				self.rh.join()
				self.q = None
				if x is not None:
					raise x[0], x[1], x[2]
				break
			yield x

	__iter__ = read_iter


def thr_iter_read(fd):
	"""Read the contents of a file as an iterator.
	The read is two-threaded, so that one thread can be
	waiting on disk I/O while the other thread is
	processing the results.
	"""
	x = threaded_readable_file(fd)
	return x.read_iter()



def makedirs(fname, mode=0775):
	"""This makes the specified directory, including all
	necessary directories above it.    It is like os.makedirs(),
	except that if the directory already exists
	it does not raise an exception.
	@param fname:Name of the directory to create.
	@param mode: Linux file permissions for any directories it needs to create.
	@type fname: L{str}
	@type mode: L{int}
	@note: If the directory already exists, it does not force it to
		have the specified C{mode}.
	@except OSError: If it cannot create a part of the directory chain.
	"""

	c = fname.split('/')
	for i in range(1+(c[0]==''), len(c)+1):
		p = '/'.join(c[:i])
		try:
			os.mkdir(p, mode)
		except OSError, e:
			if e.errno != errno.EEXIST:
				raise



def shuffle_Nrep(y, n=1, compare=None):
	"""Shuffle a list, y,
	so that no item occurs more than n times in a row.
	Equality is determined by the comparison function compare returning zero.
	"""
	import random
	assert n>0, "Silly!"
	x = list(y)
	random.shuffle(x)
	m = len(x)
	if compare is None:
		compare = lambda a, b: a==b

	passes = 0
	restart = 0
	while passes<1000:
		prb = None
		pstart = 0
		reps = 0
		# This look searches for repetitions of a line
		# in the shuffled output:
		for i in range(max(1, restart), m):
			if compare(x[i-1], x[i]):
				reps += 1
				pstart = i - 1
			else:
				pstart = None
				reps = 0
			if reps >= n:
				# Too many repetitions.
				prb = i
				break
		if prb is None:
			# If we passed the test and there aren't too many repetitions.
			y[:] = x
			return y

		k = prb+1
		# Our problem is a block of identical lines.   We need to
		# find some lines that are not identical, first.
		found = False
		while k < m:
			if not compare(x[pstart], x[k]):
				found = True
				break
			k += 1
		if not found:
			# Whoops!   The remainder of the file is stuffed with
			# identical lines.    We need to bring in some lines from
			# the beginning.
			tmp = x.pop(0)
			x.append(tmp)
			restart = 0
			continue
		# Not that we have a block containing at least some non-identical lines,
		# we shuffle that block.
		a = pstart
		b = k + 1
		# print 'a,b=', a, b
		tmp = x[a:b]
		random.shuffle(tmp)
		# print 'tmp=', x[a:b], '->', tmp
		x[a:b] = tmp
		restart = a
		passes += 1
		# Go back to the beginning to check for repetitions.
	raise RuntimeError, 'Too many passes: cannot avoid repetitions'


def testSNR():
	import random
	for i in range(20):
		x = [ i//10 for i in range(20) ]
		shuffle_Nrep(x, 1)
		for i in range(len(x)-1):
			assert x[i] != x[i+1], 'Whoops: i=%d, %d %d' % (i, x[i], x[i+1])
		x = [ i//3 for i in range(10000) ]
		random.shuffle(x)
		shuffle_Nrep(x, 1)
		for i in range(len(x)-1):
			assert x[i] != x[i+1], 'Whoops: i=%d, %d %d' % (i, x[i], x[i+1])



class dir_lock(object):
	def __init__(self, lockname):
		self.maxtries = 10
		self.name = lockname
		self.pid = os.getpid()
		self.sleep = 2.0
	
	def __enter__(self):
		locktries = 0
		d = os.path.dirname(self.name)
		if not d:
			d = '.'
		assert os.path.isdir(d), "%s is not a directory" % d
		assert os.access(d, os.W_OK|os.X_OK), "%s is not writeable" % d
		errs = set()
		while locktries < self.maxtries:
			try:
				os.mkdir(self.name)
			except OSError, x:
				errs.add(str(x))
				locktries += 1
				time.sleep(self.sleep * (((self.pid+97*locktries)%197) / 197.0)**2)
			else:
				d = None
				break
		if d is not None:
			die.warn("Could not acquire lock %s in %d tries (%s): continuing anyway." % (self.name, self.maxtries, ','.join(sorted(errs))))
			self.name = None
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if self.name:
			os.rmdir(self.name)



def open_nowipe(nm1, nm2, mode="w"):
	"""Open a file (typically for writing) but make sure that the
	file doesn't already exist.   The name is constructed from
	nm1, a sequence number, and nm2.   The sequence number gets incremented
	until a name is found that doesn't exist.
	This works by creating a directory as a lock file; it should be safe across
	NFS.
	@note: The directory containing C{nm1} must exist and be writeable.
	@param nm1: the part of the name to the left of the sequence number
	@param nm2: the part of the name to the right of the sequence number
		Typically, nm2 is a suffix like ".wav".  This may not contain a slash.
	@param mode: The way to open the file -- passed to open().
	@type nm1: str
	@type nm2: str
	@type mode: str
	@rtype C{file}
	@return: The opened L{file} object.  (Its name can be gotten from the C{name} attribute.)
	"""
	dname = os.path.dirname(nm1)
	lockf = os.path.join(dname, ".gmisclib.gpkmisc.nowipe_lock")
	with dir_lock(lockf):
        	i = 0
        	try:
                	while True:
                        	nm = '%s%d%s' % (nm1, i, nm2)
                        	open(nm, 'r')
                        	i += 1
        	except IOError:
                	pass
        	return open(nm, mode)


def dropfront(prefix, s):
	"""Drops the prefix from the string and raises an exception
	if it is not there to be dropped.
	"""
	if not s.startswith(prefix):
		raise ValueError, "String '%s' must start with '%s'" % (s[:20], prefix)
	return s[len(prefix):]


def open_compressed(fn):
	import g_pipe

	if fn.endswith('.bz2'):
		ci, co = g_pipe.popen2("bzcat", ['bzcat', fn])
		ci.close()
		return co
	elif fn.endswith('.gz'):
		ci, co = g_pipe.popen2("zcat", ['zcat', fn])
		ci.close()
		return co
	return open(fn, 'r')


def gammaln(x):
	raise RuntimeError, "Please import gammaln from gmisclib.stats"

_a_factor_cache = {1:1, 2:2, 3:3}	# THIS CACHE SHOULD BE LOCKED
def a_factor(n):	# Don't mess with private_start.
	"""Finds the smallest prime factor of a number."""

	try:
		return _a_factor_cache[n]
	except KeyError:
		pass
	for p in primes():
		if p*p > n:
			f = n
			break
		if n%p == 0:
			f = p
			break
	_a_factor_cache[n] = f
	return f


_primes = [2, 3]	# 2, 3 *must* be there.	# THIS CACHE SHOULD BE LOCKED
def primes():
	"""This is a generator that produces an infinite list of primes.
	"""
	for p in _primes:
		yield p
	i = _primes[-1] + 2
	while True:
		for p in primes():
			if p*p > i:
				if p > _primes[-1]:	# multithreading...
					_primes.append(i)
				yield i
			if i%p == 0:
				i += 2
				break


_factor_cache = {}	# THIS CACHE SHOULD BE LOCKED
def factor(n):	# Don't mess with private_start.
	"""Factor a number into a list of prime factors,
	in increasing order.
	@param n: input number
	@type n: int
	@return: prime factors
	@rtype: list
	"""

	try:
		return _factor_cache[n]
	except KeyError:
		pass
	f = a_factor(n)
	if f == n:
		tmp = [n]
	else:
		tmp = [f] + factor(n//f)
	_factor_cache[n] = tmp[:]
	return tmp


def test_primes():
	assert factor(11) == [11]
	assert factor(16) == [2, 2, 2, 2]
	assert factor(100) == [2, 2, 5, 5]
	assert factor(2) == [2]
	assert factor(97) == [97]
	assert factor(55) == [5, 11]
	assert gcd(5,3)==1
	assert gcd(14, 21)==7
	assert gcd(100, 70)==10

def gcd(a, b):
	"""Greatest common factor/denominator.
	@type a: int
	@type b: int
	@rtype: int
	@return: the greatest common factor of a and b.
	"""
	assert a >= 0 and b >= 0
	while b != 0:
		tmp = b
		b = a % b
		a = tmp
	return a



def find_in_PATH(progname):
	"""Search PATH to find where a program resides.
	@param progname: the program to look for.
	@type progname: str
	@return: the full path name.
	@rtype: str
	"""
	for p in os.environ['PATH'].split(':'):
		tmp = os.path.join(p, progname)
		if os.access(tmp, os.R_OK|os.X_OK):
			return tmp
	return None



def get_mtime(fn):
	"""Paired with L{need_to_recompute}().   These implement something like make,
	where we figure out if we need to compute things based on the age of files.
	This is used to get the age of the pre-requisites.
	@param fn: a filename or a file
	@type fn: str or file
	@return: None (if the file doesn't exist) or its modification time.
	@rtype: None or float
	"""
	try:
		if isinstance(fn, file):
			s = os.fstat(fn.fileno())
		else:
			s = os.stat(fn)
	except OSError:
		return None
	return s[stat.ST_MTIME]


class PrereqError(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)
	
	def repl(self, x):
		self.args = self.args[:-1] + (x,)


def prereq_mtime(*tlist):
	if None in tlist:
		raise PrereqError("Prerequisite has not been computed yet" , tlist.index(None))
	return max(tlist)


def need_to_recompute(fn, lazytime, size=-1):
	"""Paired with L{get_mtime}().   These implement something like make,
	where we figure out if we need to compute things.
	@param fn: a filename or a file
	@type fn: C{str} or C{file}
	@param lazytime: a time (as obtained from ST_MTIME in os.stat()).
		If the file modification time of C{fn} is older than
		C{lazytime}, recompute.
	@type lazytime: C{None} or C{float}
	@param size: recompute the file if it is smaller than C{size}.
		Normally, this is used to recompute on empty output
		files by setting C{size=0}.
	@type size: int
	@return: True if fn needs to be recomputed or if it doesn not exist.
	@rtype: bool
	"""
	if lazytime is None and size<0:
		return True
	try:
		if isinstance(fn, file):
			s = os.fstat(fn.fileno())
		else:
			s = os.stat(fn)
	except OSError:
		return True
	if size and s[stat.ST_SIZE] <= size:
		return True
	return s[stat.ST_MTIME] <= lazytime


def truncate(s, maxlen):
	assert maxlen > 3
	if len(s) < maxlen:
		return s
	return s[:maxlen-3] + '...'



#The algorithm comes from Handbook of Mathematical Functions, formula 7.1.26.
# Thanks to John D. Cook.
# http://stackoverflow.com/questions/457408/is-there-an-easily-available-implementation-of-erf-for-python
def erf(x):
	"""erf(x)=(2/sqrt(pi))*integral{0 to x of exp(-t**2) dt}"""
	# save the sign of x
	sign = 1
	if x < 0: 
		sign = -1
		x = -x
	
	# constants
	a1 =  0.254829592
	a2 = -0.284496736
	a3 =  1.421413741
	a4 = -1.453152027
	a5 =  1.061405429
	p  =  0.3275911

	# A&S formula 7.1.26
	t = 1.0/(1.0 + p*x)
	y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t*math.exp(-x*x)
	return sign*y # erf(-x) = -erf(x)



def asinh(x):
	"""Inverse hyperbolic sine."""
	if x > 0:
		sign = 1
	elif x == 0:
		sign = 0
	else:
		sign = -1
	return sign*math.log(sign*x + math.sqrt(x*x + 1))


def chooseP(x, p):
	"""Sample from a list with specified probabilities.
	@param x: a list of things from which to sample
	@type x: list(something)
	@param p: a list of probabilities for sampling the corresponding
		item of C{x}.
	@type p: C{list(float)}
	@return: a sample from C{x}
	@rtype: whatever is inside C{x}
	@raise AssertionError: Will (sometimes) detect negative probabilities,
		or probabilities that sum to something other than one.
	"""
	import random
	ps = 0.0
	r = random.random()
	for (xx, pp) in zip(x, p):
		ps += pp
		assert 0<=pp<=1.0 and ps<=1.0, "Bad probabilities"
		if pp > r:
			return xx
		else:
			r -= pp
	raise AssertionError, "Probabilities sum to %g, not 1.0" % ps


def misc_mode(lx):
	"""@return: The most common object from a list of arbitrary objects.
	@param lx: a sequence of hashable objects.
	"""
	from gmisclib import dictops
	c = dictops.dict_of_accums()
	for x in lx:
		c.add(x, 1)
	vmax = 0
	kmax = None
	for (k, v) in c.items():
		if v > vmax:
			kmax = k
			vmax = v
	if not (vmax > 0):
		raise ValueError, "Empty list"
	return kmax


def distrib(key):
	"""
	@return: The release name of the linux distribution that you're running.
	@rtype: str
	"""
	fname = '/etc/lsb-release'
	for l in open(fname, 'r'):
		l = l.strip()
		x = l.split('=')
		if len(x) == 2 and x[0]=='DISTRIB_%s' % key:
			return x[1].strip()
	raise KeyError, "Cannot find DISTRIB_%s in %s" % (key, fname)


if __name__ == '__main__':
	testCM()
	testSNR()
	test_primes()
