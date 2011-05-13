

"""This rotates a matrix by multiplying with a unitary matrix
so that the resulting elements are either nearly zero or relatively large.
It minimizes sum of |x_ij|*log(|x_ij|), i.e. the entropy (sortof).
"""

import math
from gmisclib import Num
from gmisclib import mcmc
from gmisclib import mcmc_helper
from gmisclib import gpkmisc


def make_min_entropy(x, extra_entropy=0.0):
	"""extra_entropy is a vector that helps choose what to optimize."""
	x = Num.asarray(x, Num.Float)
	print 'x.shape=', x.shape
	ndim, nvec = x.shape

	def unitary(p):
		assert p.shape[0] == nvec**2
		pm = Num.reshape(p, (nvec, nvec))
		psym = Num.dot(pm, Num.transpose(pm))
		evalues, umat = Num.LA.eigh(psym)
		return umat

	def rotated(xt, p):
		frot = Num.dot(unitary(p), xt)
		assert frot.shape == xt.shape
		return frot

	def fom(p, c):
		xt, nvec, extra_entropy, G = c
		frot = rotated(xt, p)
		assert frot.shape[0] == nvec
		# print 'frot=', frot
		frotfom = Num.absolute(frot)
		frotn = frotfom/Num.sum(frotfom, axis=1)[:,Num.NewAxis]
		assert abs(Num.sum(frotn[0])-1.0) < 0.01
		nege = Num.sum(frotn*(Num.log(frotn)-extra_entropy), axis=1)
		assert nege.shape == (nvec,)
		print 'fom=', Num.sum(nege)
		return G*Num.sum(nege)

	def fixer(p, c):
		Num.divide(p, math.sqrt(Num.average(Num.square(p))), p)
		return p

	prmvec = Num.RA.normal(0.0, 1.0, (nvec**2,))
	stpr = mcmc.bootstepper(fom, [prmvec], v=gpkmisc.make_diag(Num.square(prmvec)),
					c = (Num.transpose(x), nvec, extra_entropy, 20.0),
					fixer=fixer
					)
	mcmch = mcmc_helper.stepper(stpr)
	mcmch.run_to_bottom()
	stpr.T = 0.3
	mcmch.run_to_bottom()
	stpr.T = 0.1
	mcmch.run_to_bottom()
	prms = stpr.current().prms()
	return (Num.transpose(rotated(Num.transpose(x), prms)),
		unitary(prms)
		)


def test2():
	x = [[1.0, 1.0], [-1.0, 1.0]]
	y,u = make_min_entropy(x)
	assert abs(Num.sum(u**2) - u.shape[0]) < 0.001
	print 'y=', y
	ay = Num.absolute(y)
	assert Num.sum(Num.less(ay, 0.001)) == 2
	r2 = math.sqrt(2.0)
	assert Num.sum(Num.less(Num.absolute(ay-r2), 0.001)) == 2

def test3():
	x = [[0, 0, 1], [1.0, -1.0, 0], [1.0, 1.0, 0]]
	y,u = make_min_entropy(x)
	assert abs(Num.sum(u**2) - u.shape[0]) < 0.001
	print 'y=', y
	ay = Num.absolute(y)
	assert Num.sum(Num.less(ay, 0.01)) == 6
	r2 = math.sqrt(2.0)
	assert Num.sum(Num.less(Num.absolute(ay-r2), 0.01)) == 2
	assert Num.sum(Num.less(Num.absolute(ay-1), 0.01)) == 1


if __name__ == '__main__':
	test2()
	test3()
