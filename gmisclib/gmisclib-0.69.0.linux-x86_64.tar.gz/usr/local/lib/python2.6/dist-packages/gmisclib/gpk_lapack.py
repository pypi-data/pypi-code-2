
import Numeric

class NoSolutionError(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)

def solve(a, b0):
	""" solves a*x = b."""
	b = Numeric.asarray(b0, Numeric.Float)
	if len(b.shape) == 1:
		b = Numeric.array((b,), Numeric.Float)
	# print "b.shape=", b.shape
	assert a.n == b.shape[1]
	import lapack_dpb
	# print "type(a.d)==", type(a.d)
	# print "a.d=", a.d
	# print "ravel(a.d)=", Numeric.ravel(a.d)
	# print "a.ldab=", a.ldab
	result = lapack_dpb.dpbsv('L', a.n, a.kd, b.shape[0], a.d,
					a.ldab, b, max(1, a.n), 0)
	# print "result=", result
	if result['info'] != 0:
		raise NoSolutionError, 'Linear system has no solution. Lapack_dpb.dpbsv info code=%d' % result['info']
	# print "b=", b
	return b


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
		assert None


def err(a, b):
	return Numeric.sum(Numeric.square(a-b))

def test2():
	x = sbd(6,2)
	b = Numeric.zeros((6,), Numeric.Float) + 10
	for i in range(6):
		x[i,i] = 2
	x[2,1] = 0.5
	# print "x=", x
	y = solve(x, b)
	y_t = Numeric.array(([5, 4, 4, 5, 5, 5],))
	# print "y=", y, "y_t=", y_t
	# print "x=", x
	assert err(y_t, y) < 1e-9


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
	y = Numeric.array([[1, 2], [2, 3]])
	x.bd_increment(1, y)
	assert x[1,1]==1
	assert x[2,2]==3
	assert x[2,1]==2
	assert x[1,2]==2
	assert x[0,0]==0
	assert x[3,3]==0
	assert x[3,2]==0
	z = Numeric.array([[-1, 0, 1], [0, 0, 0], [0, 0, 0]])
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
