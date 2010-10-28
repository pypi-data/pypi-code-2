
"""Does a robust estimate of covariance.
It doesn't converge, unfortunately, for
vectors of dimension higher than 1.
"""

import Num
import math
import sys
import die

def cov_wt(veclist, weights):
	nvec,vecdim = veclist.shape
	o = Num.zeros((vecdim,vecdim), Num.Float)
	for i in range(nvec):
		Num.add(o, Num.outerproduct(veclist[i], veclist[i])*weights[i], o)
	Num.divide(o, Num.sum(weights), o)
	return o


def integrate_guts(xlow, xhigh, fcn, c, n):
	sum = 0.0
	dx = (xhigh-xlow)/float(n)
	for i in range(n):
		x = xlow + (i+0.5)*dx
		sum += fcn(x, c)
	return sum*dx


def integrate(xlow, xhigh, fcn, c=None, nstart=5, tol=1e-4):
	"""A generally useful function, does the integral of
	fcn(x, c) from xlow to xhigh.
	"""
	passes = 0
	while passes < 10:
		i = integrate_guts(xlow, xhigh, fcn, c, nstart)
		tmp = integrate_guts(xlow, xhigh, fcn, c, nstart*3)
		if abs(tmp-i) < tol:
			return tmp + (tmp-i)/9.0
		nstart *= 3
		i = tmp
		passes += 1
	raise RuntimeError, "Integral doesn't converge"


def wtfunc(q, E):
	Qcut = 2.0
	return (Qcut/(Qcut + q))**E
	# return Num.minimum(1.0, q**(-E))


def wtdim(q, Edim):
	E,vecdim,qxtra = Edim
	q2 = q**2
	return math.exp(-q2/2.0)*wtfunc(q2,E) * q**qxtra


def covariance(veclist, emax=1.0):
	"""Veclist[i] is a vector.
	"""
	echg = 0.25
	E = echg * emax
	nvec, vecdim = veclist.shape
	e0 = integrate(0, 3.0+0.5*vecdim, wtdim, c=(0.0,vecdim, 0),
					nstart = vecdim*2)
	e0qq = integrate(0, 3.0+0.5*vecdim, wtdim, c=(0.0,vecdim, 2),
					nstart = vecdim*2)
	# Qtol = SMALL * NDIM * WIDTH_OF_CHISQ(ndim)_DISTRIBUTION
	qtol = 0.001*nvec*math.sqrt(vecdim)
	weights = Num.ones((len(veclist),), Num.Float)
	efac = 1.0
	qlast = None
	ipass = 0
	while ipass < 1000:
		c = cov_wt(veclist, weights) / efac
		assert c.shape == (vecdim, vecdim)
		print 'c.shape=', c.shape
		print 'c=', c
		eval, evec = Num.LA.eigh(c)
		print 'evals=', eval
		if not Num.alltrue(eval >= 0.0):
			weights = Num.sqrt(weights)
			die.warn('Negative eigenvalue: slowing down.')
			continue
		ichalf = evec/Num.sqrt(eval)
		# print 'ERR=', Num.dot(Num.transpose(ichalf), Num.dot(c, ichalf))
		# print 'ichalf=', ichalf
		vecxf2 = Num.dot(veclist, ichalf)**2
		print 'vecxf2=', vecxf2
		assert vecxf2.shape == (nvec, vecdim)
		weighttmp = wtfunc(vecxf2, E)
		print 'weighttmp=', weighttmp
		weights = Num.prod(weighttmp, axis=1)
		assert weights.shape == (nvec,)
		q = Num.sum(vecxf2, axis=1)
		assert q.shape == (nvec,)
		print 'q=', q
		assert Num.alltrue(q >= 0.0)
		print 'weight=', weights
		if qlast is not None:
			qchg = Num.sum(Num.absolute(q-qlast))
			echg = 1.0/math.sqrt(qchg/qtol + 1.0)
			print 'qchg=', qchg, 'echg=', echg, 'E=', E
			if qchg < qtol and abs(E-emax)<0.01:
				return (c, eval, evec, q)
		qlast = q
		e = integrate(0, 3.0+0.5*vecdim, wtdim, c=(E,vecdim,0),
					nstart = vecdim*2)
		eqq = integrate(0, 3.0+0.5*vecdim, wtdim, c=(E,vecdim,2),
					nstart = vecdim*2)
		efac = (eqq/e0qq)/(e/e0)
		print 'efac=', efac
		E = echg*emax + (1.0-echg)*E
		ipass += 1
		sys.stdout.flush()
	raise RuntimeError, "Covariance does not converge."


if __name__ == '__main__':
	Nvec = 2000
	ND = 10
	veclist = Num.RA.normal(0.0, 1.0, (Nvec,ND))
	covariance(veclist)
