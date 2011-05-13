import Num
import types

import sbd_array

class BadParamError(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)

class NoTermsEx(ValueError):
	def __init__(self, s='Empty Equation'):
		ValueError.__init__(self, s)

class eqn_c:
	def index_ends(self):
		if len(self.terms) == 0:
			raise NoTermsEx
		return (self.terms[0][0], self.terms[-1][0])

	def __init__(self, terms, sum, wt, index_ctr):
		"""Takes an equation in the form:
		[(index, coefficient), ...] = sum
		and stores it away into a class.
		"""
		if type(terms) != types.ListType:
			raise TypeError, 'first arg to eqn_c is a list'
		if type(index_ctr)!=types.IntType:
			raise TypeError, 'index_ctr in eqn_c is a int'
		if wt < 0:
			raise BadParamError, 'wt<0'
	
		# for t in terms:
			# assert type(t[0])==types.IntType, 'Not int index: T=%s'%str(t)
		self.terms = map(lambda x, w=wt, c=index_ctr: (x[0]+c, x[1]*w),
					terms)
		self.terms.sort()	# Tuples are sorted by their first element first.
		self.sum = sum*wt

	def __str__(self):
		termlist = map(lambda x: "%g*x[%d] "%(x[1], x[0]), self.terms)
		return '<eqn_c: ' + ' '.join(termlist) + " = %g >"%self.sum

	def substitute(self, known, zero=0):
		"""Modifies an equation by substituting in known values.
		Argument 'known' is an array of values."""
		try:
			sis, sie = self.index_ends()
		except NoTermsEx:
			return
		if sis >= zero:
			return
		o = []
		for t in self.terms:
			if t[0] >= zero :
				o.append(t)
			else:
				# print "substitute: known[", t[0], "]=", known[t[0]-zero]
				try:
					self.sum = self.sum - t[1]*known[t[0]-zero]
				except IndexError:
					raise RuntimeError, "Sorry. Previous phrase too short or smooth too big."
				# Here we make use of the fact that known[-1] == the last value
		self.terms = o
				
	def __nonzero__(self):
		return len(self.terms)>0



def range_of_indices(l):
	"""This finds the highest and lowest indices for a list of equations."""
	xmin = []
	xmax = []
	for q in l:
		try:
			t = q.index_ends()
		except NoTermsEx:
			continue
		xmax.append(t[1])
		xmin.append(t[0])
	return (min(xmin), max(xmax))


def bandwidth(l):
	bw = 0
	for q in l:
		try:
			ts, te = q.index_ends()
		except NoTermsEx:
			continue
		tmp = te - ts
		if tmp > bw:
			bw = tmp
	return bw

def build_matrices(l, n=None, maxbw=None):
	"""Takes a list of eqn_c classes, and builds the
	matrices to be solved.
	"""
	m = len(l)
	if n is None:
		t = range_of_indices(l)
		assert t[0] == 0
		n = t[1] + 1
	b = Num.zeros((n,), Num.Float)

	if maxbw is None:
		maxbw = bandwidth(l)
	a = sbd_array.sbd(n, maxbw)

	for e in l:
		try:
			ts, te = e.index_ends()
		except NoTermsEx:
			continue
		assert ts >= 0 and te < n
		tt = Num.zeros((te-ts+1,), Num.Float)
		for (t10, t11) in e.terms:
			idx = t10 - ts
			tt[idx] = tt[idx] + t11
			b[t10] = b[t10] + t11 * e.sum
		block = Num.multiply.outer(tt, tt)
		a.bd_increment(ts, block)
	return (a, b)



def test_eqn():
	e0 = []
	e0.append(eqn_c([(0,1)], 3.0, 2.0, 0))
	a, b = build_matrices(e0)
	# print "a=", a
	# print "b=", b
	assert a.shape == (1, 1)
	assert a[0,0] == 4.0
	assert b[0] == 12.0


def add_something(a, thing, scale):
	"""Add a band-diagonal part to matrix a.
	We assume a has shared-reference semantics, like
	the Numeric module.  This will *not* work for sbd_array,
	which has copy semantics for __getslice__.
	"""
	nt = len(thing)
	assert a.shape[0] == a.shape[1]
	assert a.shape[0] > 2*nt+1
	c = map(lambda x, sc=scale: Num.asarray(x)*sc, thing)
	ash = a.shape
	for i in range(nt-1):
		assert len(c[i].shape)==1
		aslice = a[i, 0:c[i].shape[0]]
		Num.add(aslice, c[i], aslice)
		eslice = a[-1-i, -1:-c[i].shape[0]-1:-1]
		Num.add(eslice, c[i], eslice)

	assert c[-1].shape[0]%2 == 1
	hmm = c[-1].shape[0]/2
	assert hmm == nt-1

	cnt = c[nt-1]
	for i in range(hmm, ash[0]-hmm):
		aslice = a[i,i-hmm:i+hmm+1]
		Num.add(aslice, cnt, aslice)

	return 1 + hmm


def add_slope_curv_droop(a, sls, cs, droop):
	"""Adds a slope and curvature part to the matrix.
	Returns the bandwidth of the part it added.
	"""
	add_something(a, [[1]], droop)
	add_something(a, [[1, -1], [-1, 2, -1]], sls)
	add_something(a, [[-1, 2, -1],
				[-2, 5, -4, 1],
				[1, -4, 6, -4, 1]], cs)




def full_matrices(l, n, sls, cs, droop):
	a, b = build_matrices(l, n)
	add_slope_curv_droop(a, sls, cs, droop)
	return (a, b)



def solve_eqns(a, b):
	return sbd_array.solve(a, b)




def test_solve():
	e = []
	e.append(eqn_c([(0,2)], 1.0, 1.0, 0))
	e.append(eqn_c([(0,1)], 2.0, 1.0, 1))
	a, b = build_matrices(e)
	# print "a=", a
	# print "b=", b
	x = solve_eqns(a, b)
	# print "x=", x
	assert x[0,0] == 0.5
	assert x[0,1] == 2.0
	e = []
	e.append(eqn_c([(0,1), (1,1)], 1.0, 1.0, 0))
	e.append(eqn_c([(0,-1), (1,1)], 1.0, 1.0, 0))
	a, b = build_matrices(e)
	x = solve_eqns(a, b)
	# print "x=", x
	assert abs(x[0,0]) < 1e-6
	assert abs(x[0,1] - 1) < 1e-6
	e = []
	e.append(eqn_c([(0,1)], 1.0, 2.0, 0))
	e.append(eqn_c([(0,1)], 2.0, 1.0, 0))
	a, b = build_matrices(e)
	x = solve_eqns(a, b)
	# print "a=", a, "b=", b, "x=", x
	assert abs(x[0,0] - 6./5.) < 1e-6

def test_solve2():
	e = []
	e.append(eqn_c([(0,-1), (1,1)], 1.0, 1.0, 0))
	e.append(eqn_c([(0,-1), (1,1)], 1.0, 1.0, 1))
	e.append(eqn_c([(0,-1), (1,1)], 1.0, 1.0, 2))
	e.append(eqn_c([(0,1)], 1.0, 1.0, 0))
	# e.append(eqn_c([(0,1)], 1.0, 1.0, 0))
	a, b = build_matrices(e)
	# print "a=", a
	# print "b=", b
	x = solve_eqns(a, b)
	# print "x=", x
	assert x.shape == (1, 4)
	assert abs(x[0,0] - 1) < 1e-6
	assert abs(x[0,1] - 2) < 1e-6
	assert abs(x[0,2] - 3) < 1e-6
	assert abs(x[0,3] - 4) < 1e-6

def test_bw():
	e = []
	e.append(eqn_c([], 0.0, 1.0, 0))
	assert bandwidth(e) == 0
	e.append(eqn_c([(0,-1), (1,1)], 1.0, 1.0, 0))
	assert bandwidth(e) == 1



def test_as():
	"""Won't work for sbd_array."""
	a = Num.zeros((10,10), Num.Float)
	add_something(a, [[1, -1], [2, -4, 2]], 1.0)
	# print a
	assert a[0,0] == 1
	assert a[0,1] == -1
	assert a[-1,-1] == 1
	for i in range(2, 8):
		assert a[i,i] == -4
		assert a[i-1, i] == 2
		assert a[i+1, i] == 2
		assert a[i, i-1] == 2
		assert a[i, i+1] == 2



def test():
	test_as()
	test_eqn()
	test_solve()
	test_solve2()
	test_bw()


if __name__ == '__main__' :
	test()
	# print "OK: passed tests"
