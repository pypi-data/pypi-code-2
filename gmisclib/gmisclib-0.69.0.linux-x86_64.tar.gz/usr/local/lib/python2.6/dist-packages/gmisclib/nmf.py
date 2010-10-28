"""V=WH, where W and H are non-negative.

From D. D. Lee and H. S. Seung, 'Learning the parts of objects by
nonnegative matrix factorization.'
"""

import Num
import math
import die



EPS = 1e-6
CC = 2
IEPS = 0.03

def _norm(x):
	try:
		tmp = math.sqrt(Num.sum(x**2, axis=None))
	except OverflowError, x:
		print "x=", x
		raise
	return tmp
	

def _converged(wh, whold, v, fudge):
	F = math.sqrt(wh.shape[0] * wh.shape[1])
	d1 = _norm(wh-whold)/_norm(v)
	d2 = _norm(v-wh)/_norm(v)
	die.dbg("Converged= %f %f" % (d1, d2))
	return min(d1*F,d2) < EPS*fudge


def _updateH(w, h, wh, v):
	# eps = EPS*(Num.sum(v)
	eps = EPS * Num.sum(wh, axis=None)/(v.shape[0]*v.shape[1])
	# f = Num.matrixmultiply(Num.transpose(w), (v+eps)/(wh+eps))
	f = Num.matrixmultiply(Num.transpose(w), v/(wh+eps))
	# print "H: f=", f
	return h * f


def _updateW(w, h, wh, v):
	eps = EPS * Num.sum(wh, axis=None)/(v.shape[0]*v.shape[1])
	print 'eps=', eps
	# f = Num.matrixmultiply((v+eps)/(wh+eps), Num.transpose(h))
	f = Num.matrixmultiply(v/(wh+eps), Num.transpose(h))
	print 'f=', f
	print "W:v/wh=", v/(wh+eps)
	print "W:f=", f
	new_w = w * f
	print "new_w=", new_w
	first_index_sum = Num.sum(new_w, axis=0)
	print "fis=", first_index_sum
	print 'new_w=', new_w
	o = new_w/first_index_sum[Num.NewAxis, :]
	print "o=", o
	return o


def _initialize(v, rank):
	n, m = v.shape
	w = Num.RA.standard_normal((n, rank))**2 + IEPS
	c = Num.sum(v**2, axis=0)/(v.shape[0]*v.shape[1])
	h = c * (Num.RA.standard_normal((rank, m))**2 + IEPS)
	return (w, h)


def nmf(v, rank):
	assert rank > 0, "Zero rank approximations are usually pretty awful."
	v = Num.asarray(v, Num.Float)
	assert Num.alltrue(Num.greater_equal(Num.ravel(v), 0.0)), "Negative element!"
	w, h = _initialize(v, rank)
	cc = 0
	ic = 0
	wh = Num.zeros(v.shape, Num.Float)
	while 1:
		# die.dbg("Loop, cc= %d" % cc)
		whold = wh
		wh = Num.matrixmultiply(w, h)
		if _converged(wh, whold, v, math.sqrt(ic/float(rank))):
			cc += 1
		else:
			cc = 0
		# print "cc=", cc
		if cc > CC:
			break
		wnew = _updateW(w, h, wh, v)
		hnew = _updateH(w, h, wh, v)
		w = wnew
		h = hnew
		ic += 1

	return (w, h, _norm(v - Num.matrixmultiply(w, h)) )




def _test1():
	a = [[1, 0], [1, 0], [0, 0]]
	w, h, err = nmf(a, 1)
	wh = Num.matrixmultiply(w, h)
	assert _norm(wh - a) < 30*EPS
	assert err<0.001

def _test2():
	a = [[1, 0], [0, 1], [0, 0]]
	w, h, err = nmf(a, 2)
	wh = Num.matrixmultiply(w, h)
	assert _norm(wh - a) < 30*EPS
	assert err<0.001


def _test3( rank ):
	a = [[1.0, 0.0, 0.5], [0.0, 1.0, 0.5], [1.0, 1.0, 1.0]]
	w, h, err = nmf(a, rank)
	wh = Num.matrixmultiply(w, h)
	assert _norm(wh - a) < 30*math.sqrt(EPS)
	assert err<0.001


if __name__ == '__main__':
	print "TEST1"
	_test1()
	print
	print "TEST2"
	_test2()
	print
	print "TEST3(1)"
	try:
		_test3(1)
	except AssertionError:
		pass
	else:
		raise AssertionError, "Test3(1) should fail!"
	print
	print "TEST3(2)"
	_test3(2)
	print
	print "TEST3(3)"
	_test3(3)
	print
	print "TEST3(4)"
	_test3(4)
	# print
	print "TEST3(5)"
	_test3(5)
	print
	print "LAST"

	a = [[1, 0], [0, 1]]
	w, h, err = nmf(a, 4)
	print "w=", w
	print "h=", h
	print "wh=", Num.matrixmultiply(w, h)
	print "a=", a
