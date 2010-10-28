"""Resample a time series by a factor r.  I.e. sample more
densely (r<1) or less densely (r>1).
Also see tsops.py."""


import Num


def simple(a, r, direction=0):
	aa = Num.array(a)
	newlen = 1 + int((aa.shape[direction]-1)/r)
	t = Num.around(Num.arrayrange(newlen)*r)
	# print "t=", t
	aswap = Num.swapaxes(aa, direction, 0)
	interped = Num.choose(t, aswap)
	return Num.swapaxes(interped, direction, 0)


def compare(a, b):
	assert len(a) == len(b)
	for i in range(len(a)):
		assert(a[i] == b[i])


def test():
	x = simple([0,1,2,3,4,5,6,7,8,9], 2.0)
	compare(x, [0, 2, 4, 6, 8])
	x = simple([0, 1, 2, 3, 4], 0.5)
	compare(x, [0, 1, 1, 2, 2, 3, 3, 4, 4])


if __name__ == '__main__':
	test()
