# -*- coding: utf-8 -*-
"""Solves various equations involving minimizing the
sum of absolute values of things.
"""


import math
import numpy
from gmisclib import Numeric_gpk
from gmisclib import root
from gmisclib import weighted_percentile as WP

def solve1(y0, y1):
	"""We minimize the equation sum_over_i(abs(y0_i*(1-x) + y1_i*x))
	to find the best x.   Returns x.
	I don't know if this is strictly correct.
	"""
	n = len(y0)
	assert len(y1)==n
	yy0 = numpy.asarray(y0)
	yy1 = numpy.asarray(y1)
	slp = yy1-yy0
	zro = -yy0/slp
	i = numpy.argsort(zro)
	zros = numpy.take(zro, i, axis=0)
	slps = numpy.absolute(numpy.take(slp, i, axis=0))
	islps = numpy.add.accumulate(slps)
	isl_tgt = 0.5*islps[-1]
	minidx = numpy.searchsorted(islps, [isl_tgt])
	return zros[minidx]


def solve_fit(x, y, epsx=1e-7, epsm=1e-7):
	"""Solves for the line yhat = m*x + b that minimizes
	sum(abs(y - yhat)).   In other words, it's a fit to a straight line,
	but a highly robust fit that will not be disturbed by outliers.
	The algorithm is from Numerical Recipes, Volume 2.
	@param epsx: a tolerance used in the iterative solution.
		Eps is roughly the required accuracy of the x-intercept of the solution,
		expressed as a fraction of the x-range of the data.
	@param epsm: a tolerance used in the iterative solution.  Roughly,
		it is the accuracy of C{m} in the solution.  Note the tangent() call!
	@type epsx: C{float}
	@type epsm: C{float}
	@return: (mhat, bhat), where mhat*x+bhat is the best fit to the data.
	@rtype: C{tuple(float,float)}
	"""
	assert epsx > 0.0
	x = numpy.asarray(x)
	xbar = numpy.average(x)
	x = x - xbar
	y = numpy.asarray(y)
	ybar = numpy.average(y)
	y = y - ybar


	def b(x, y, m):
		b = y - m*x
		return numpy.median(b)

	mp2 = math.pi / 2.0

	def to_be_zeroed(theta, xy):
		x, y = xy
		# print 'SSA: x=', x
		# print 'SSA: y=', y
		if theta == mp2:
			# print 'SSA: tmp=', numpy.sum(x* -numpy.sign(x)), 'theta=', theta
			return numpy.sum(-numpy.sign(x)*x)
		if theta == -mp2:
			# print 'SSA: tmp=', numpy.sum(x*numpy.sign(x)), 'theta=', theta
			return numpy.sum(x * numpy.sign(x))

		m = math.tan(theta)
		bhat = b(x, y, m)
		tmp = numpy.sum(x * numpy.sign(y - m*x - bhat) )
		# print 'SSA: tmp=', tmp, 'm=', m, 'bhat=', bhat
		return tmp

	xtol = epsx*numpy.sum(numpy.absolute(x))
	mhat =  math.tan( root.root(to_be_zeroed, -mp2, mp2, (x, y),
					epsm, xtol
					)
			)
	return (mhat, b(x, y, mhat)+ybar-mhat*xbar)
	
	
	
def solve_fit_wt(x, y, wt, epsx=1e-7, epsm=1e-7):
	"""Solves for the line yhat = m*x + b that minimizes
	sum(abs(y - yhat)).   In other words, it's a fit to a straight line,
	but a highly robust fit that will not be disturbed by outliers.
	The algorithm is from Numerical Recipes, Volume 2.
	@param epsx: a tolerance used in the iterative solution.
		Eps is roughly the required accuracy of the x-intercept of the solution,
		expressed as a fraction of the x-range of the data.
	@param epsm: a tolerance used in the iterative solution.  Roughly,
		it is the accuracy of C{m} in the solution.  Note the tangent() call!
	@type epsx: C{float}
	@type epsm: C{float}
	@return: (mhat, bhat), where mhat*x+bhat is the best fit to the data.
	@rtype: C{tuple(float,float)}
	"""
	assert epsx > 0.0
	if not numpy.greater_equal(wt, 0.0).all():
		raise ValueError, "Weights must be non-negative."
	sw = numpy.sum(wt)
	if not (sw > 0.0):
		raise ValueError, "Weights are NaN or all zero"
	x = numpy.asarray(x)
	xbar = numpy.sum(x*wt)/sw
	x = x - xbar
	y = numpy.asarray(y)
	ybar = numpy.sum(y*wt)/sw
	y = y - ybar

	def b(x, y, wt, m):
		b = y - m*x
		return WP.wp(b, wt, [0.5])[0]

	mp2 = math.pi / 2.0

	def to_be_zeroed(theta, xyw):
		x, y, wt = xyw
		# print 'SSA: x=', x
		# print 'SSA: y=', y
		if theta == mp2:
			# print 'SSA: tmp=', numpy.sum(x* -numpy.sign(x)), 'theta=', theta
			return numpy.sum(-numpy.sign(x)*wt*x)/sw
		if theta == -mp2:
			# print 'SSA: tmp=', numpy.sum(x*numpy.sign(x)), 'theta=', theta
			return numpy.sum(x * numpy.sign(x) * wt)/sw

		m = math.tan(theta)
		bhat = b(x, y, wt, m)
		tmp = numpy.sum(x * numpy.sign(y - m*x - bhat) * wt )/sw
		# print 'SSA: tmp=', tmp, 'm=', m, 'bhat=', bhat
		return tmp

	xtol = epsx * numpy.sum(numpy.absolute(x)*wt) / sw
	mhat =  math.tan( root.root(to_be_zeroed, -mp2, mp2, (x, y, wt),
					epsm, xtol
					)
			)
	return (mhat, b(x, y, wt, mhat)+ybar-mhat*xbar)



def test1():
	assert solve1([-1], [1]) == 0
	assert solve1([0.5, 1], [0.1, 0]) == 1
	assert solve1([1.1, 0.6], [0, 0.1]) == 1


def test2():
	m, b = solve_fit([0,1], [0,1])
	assert abs(b-0.0)<0.0001 and abs(m-1.0)<0.0001
	m, b = solve_fit([0,0], [1,1])
	assert abs(b-1.0)<0.0001
	m,b = solve_fit([0,1], [0,0.5])
	assert abs(b-0.0)<0.0001 and abs(m-0.5)<0.0001
	m,b = solve_fit([0,1], [1,3])
	assert abs(b-1.0)<0.0001 and abs(m-2.0)<0.0001
	m,b = solve_fit([0,1,2], [1,-1,-3])
	assert abs(b-1.0)<0.0001 and abs(m+2.0)<0.0001
	m,b = solve_fit([0.0, 1.0, 1.0, 2.0], [0.0, 0.0, 2.0, 2.0])
	assert abs(b-0.0)<0.0001 and abs(m-1.0)<0.0001
	m,b = solve_fit([0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 2.0, 3.0], [0.0, 1.0, 0.9, 2.0, 1.1, 2.0, 3.0, 4.0])
	assert abs(b-1.0)<0.0001 and abs(m-1.0)<0.0001
	m,b = solve_fit([0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 6.0, 7.0], [0.0, 1.0, 0.9, 2.0, 1.1, 6.0, 7.0, 8.0])
	assert abs(b-1.0)<0.0001 and abs(m-1.0)<0.0001
	m,b = solve_fit([0.0, 0.0, 0.0, 5.0, 6.0, 7.0], [1.0, 1.1, 0.9, 6.0, 7.0, 8.0])
	assert abs(b-1.0)<0.0001 and abs(m-1.0)<0.0001

if __name__ == '__main__':
	test1()
	test2()
