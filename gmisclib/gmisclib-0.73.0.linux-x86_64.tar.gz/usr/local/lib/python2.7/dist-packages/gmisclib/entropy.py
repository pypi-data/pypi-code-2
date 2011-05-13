#!/usr/bin/env python

import math
import random
from gmisclib import Num
from gmisclib import mcmc
from gmisclib import mcmc_helper
import gpkavg
from gmisclib import gpkmisc

def P(x):
	assert Num.alltrue(x >= 0)
	sx = Num.sum(x, axis=0)
	return x/sx


def multinomial_logp(x, cF):
	assert len(x.shape) == 1
	c, F = cF
	assert len(c.shape) == 1
	assert x.shape == c.shape
	if Num.sometrue(x <= 0):
		return None
	sx = Num.sum(x, axis=0)
	xe = x / sx
	assert len(xe.shape) == 1
	log_combinations = gpkmisc.log_factorial(Num.sum(c, axis=0))
	for cc in c:
		log_combinations -= gpkmisc.log_factorial(cc)
	normc = x.shape[0] * math.log(sx)**2
	rv = (Num.sum(Num.log(xe)*c, axis=0) + log_combinations - normc) * F
	return rv


def multinomial_fixer(x, c):
	EPS = 1e-8
	while Num.sometrue( x <= 0.0):
		for i in Num.nonzero( x <= 0.0):
			x[i] = -x[i] + EPS
	return x


def information_gained(c, pc=None):
	"""Suppose there is an experiment where you have N conditions
	and in each conditions there are M possible measurements.
	The outcomes are represented by c[N,M] matrix of counts:
	how many times you observe each possible measurement for each
	condition.

	We want to ask what's the information gained by taking
	a measurement.     We assume the probability of
	each condition is a pc[N] vector, which defaults to the
	frequencies in c.  (We assume that the choice of condition is
	not a random variable, but is made in advance, like most
	experiments.)
	"""
	EPS = 1e-6
	F = 1.0

	c = Num.asarray(c, Num.Int)
	N,M = c.shape
	if pc is not None:
		pc = Num.asarray(pc, Num.Float)
	else:
		print 'c=', c
		print 'NS(c)', Num.sum(c+0.5, axis=1)
		pc = Num.sum(c+0.5, axis=1)/Num.sum(c+0.5)
		print 'pc=', pc
		assert pc.shape == (N,)
	assert abs(Num.sum(pc)-1) < EPS

	K = 2*Num.sum(c) + 10
	K2 = int(round(math.sqrt(K)) + 10)
	pstart = (0.5+c) / Num.sum(0.5+c, axis=0)
	tmpP = []
	for i in range(N):
		pV = 0.1*Num.identity(M)/float(M)**1.5
		xp = mcmc.bootstepper(multinomial_logp, pstart[i,:], pV,
					c=(c[i,:],F), fixer=multinomial_fixer)
		s = mcmc_helper.stepper(xp)
		s.run_to_bottom()
		print 'RTB'
		s.run_to_ergodic(5.0)
		print 'RTE'
		tmp = []
		for j in range(K2):
			s.run_to_ergodic(1.0)
			tmp.append( P(xp.prms()) )
		tmpP.append(tmp)
	print 'Q'
	assert len(tmpP) == N
	tmpe = []
	for j in range(K):
		prior = Num.zeros((M,), Num.Float)
		epost = 0.0
		for i in range(N):
			pi = random.choice(tmpP[i])
			assert abs(Num.sum(pi)-1.0) < 0.001
			Num.add(prior, pi*pc[i], prior)
			epost -= pc[i]*Num.sum(Num.log(pi)*pi)
		assert abs(Num.sum(prior)-1.0) < 0.001
		eprior = -Num.sum(Num.log(prior)*prior)
		tmpe.append( eprior - epost )
	print 'R'
	avg, sigma = gpkavg.avg(tmpe, None, 0.0001)
	return (avg, sigma)

if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass
	print information_gained(
		[[0,0,10],[0,0,10],[0,0,10]]
		)
