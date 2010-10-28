
"""Suppose there is a random variable with true distribution p.
Then (as we will see) we could represent that random variable with a code that has average length H(p).
However, due to incomplete information we do not know p;
instead we assume that the distribution of the random variable is q.
Then (as we will see) the code would need more bits to represent the random variable.
The difference in the number of bits is denoted as D(p|q).
The quantity D(p|q) comes up often enough that it has a name: it is known as the relative entropy::

	The relative entropy or Kullback-Leibler distance between two
	probability mass functions p(x) and q(x) is defined as
	D(p||q) = Sum{x in X} p(x) log(p(x)/q(x))

Note that this is not symmetric, and the q (the second argument) appears only in the denominator.
"""

import Num
import mcmc
import mcmc_helper
import gpkavg
import gpkmisc
import math
import random

def P(x):
	assert Num.alltrue(x >= 0)
	sx = Num.sum(x, axis=0)
	return x/sx


def multinomial_logp(x, cF):
	c, F = cF
	assert x.shape == c.shape
	if Num.sometrue(x <= 0):
		return None
	sx = Num.sum(x, axis=0)
	xe = x / sx
	log_combinations = gpkmisc.log_factorial(Num.sum(c, axis=0))
	for cc in c:
		log_combinations -= gpkmisc.log_factorial(cc)
	normc = x.shape[0] * math.log(sx)**2
	return (Num.sum(Num.log(xe)*c, axis=0) + log_combinations - normc) * F


def multinomial_fixer(x, c):
	EPS = 1e-8
	while Num.sometrue( x <= 0.0):
		for i in Num.nonzero( x <= 0.0):
			x[i] = -x[i] + EPS
	return x


def kl_nonzero_probs(p, q):
	"""Kullback-Lieber distance between two normalized,
	nonzero probability distributions."""
	# print 'kl_nonzero_probs:', p, q
	rv = Num.sum( kl_nonzero_prob_m(p, q), axis=0 )
	# print '     result=', rv
	return rv


def kl_nonzero_prob_m(p, q):
	rv = p*Num.log(p/q) / math.log(2.0)
	return rv


def kldist_vec(p, q, N=None, Fp=1.0, Fq=1.0, Clip=0.01):
	"""Relative entropy or Kullback-Liebler distance between
	two frequency distributions p and q.
	Here, we assume that both p and q are counts
	derived from multinomial distributed data;
	they are not normalized to one.
	"""

	p = Num.asarray(p, Num.Int)
	q = Num.asarray(q, Num.Int)
	assert p.shape == q.shape
	if N is None:
		N = p.shape[0]**2 * 30
	assert Num.sum(p) > 0
	assert Num.sum(q) > 0
	qstart = ((0.5+q)/Num.sum(0.5+q, axis=0))
	pstart = ((0.5+p)/Num.sum(0.5+p, axis=0))
	pV = 0.1*Num.identity(p.shape[0])/float(p.shape[0])**1.5
	qV = 0.1*Num.identity(q.shape[0])/float(q.shape[0])**1.5
	xq = mcmc.bootstepper(multinomial_logp, qstart, qV,
				c=(q,Fq), fixer=multinomial_fixer)
	xp = mcmc.bootstepper(multinomial_logp, pstart, pV,
				c=(p,Fp), fixer=multinomial_fixer)
	mcmchp = mcmc_helper.stepper(xp)
	mcmchq = mcmc_helper.stepper(xq)
	mcmchp.run_to_bottom()
	mcmchp.run_to_ergodic(5.0)
	mcmchq.run_to_bottom()
	mcmchq.run_to_ergodic(5.0)
	o = []
	for i in range(N):
		mcmchp.run_to_ergodic(1.0)
		mcmchq.run_to_ergodic(1.0)
		o.append( kl_nonzero_probs(P(xp.prms()), P(xq.prms())) )
	avg, sigma = gpkavg.avg(o, None, Clip)
	return (avg, sigma)


def tr_from_obs(x):
	"""Given a matrix of P(i and j) as x[i,j],
	we compute P(j given i) and return it as y[i,j].
	The result is a transition probability matrix
	where the first index is the input state, and the second
	index marks the result state.
	"""
	# print 'tr_from_obs:', x
	assert x.shape[0] == x.shape[1]
	y = Num.zeros(x.shape, Num.Float)
	for i in range( x.shape[0] ):
		sxi = Num.sum( x[i], axis=0 )
		assert sxi > 0
		y[i] = x[i] / sxi
	# print '\ttr_from_obs:', y
	return y


def estimate_tr_probs(counts, N, F=1.0):
	n = counts.shape[0]
	assert counts.shape == (n,n)
	q = Num.ravel(counts)
	assert Num.alltrue(Num.equal(Num.reshape(q, (n,n)), counts))
	assert Num.sum(q) > 0
	qstart = ((0.5+q)/Num.sum(0.5+q, axis=0))
	qV = 0.1*Num.identity(q.shape[0])/float(q.shape[0])**1.5
	xq = mcmc.bootstepper(multinomial_logp, qstart, qV,
				c=(q,F), fixer=multinomial_fixer)
	mcmch = mcmc_helper.stepper(xq)
	mcmch.run_to_bottom()
	mcmch.run_to_ergodic(5.0)
	o = []
	for i in range(N):
		mcmch.run_to_ergodic(1.0)
		# print 'xq.prms=', xq.prms()
		est_p_obs = Num.reshape(xq.prms(), (n,n)) / Num.sum( xq.prms(), axis=0 )
		tmptr = tr_from_obs( est_p_obs )
		# print '# tmptr=', tmptr
		o.append( tmptr )
	return o


class NoConvergenceError(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)

class NotMarkovError(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)

def solve_for_pi(p):
	"""Given a transition probability matrix p,
	where the first index is the initial state
	and the second index is the resultant state,
	compute the steady-state probability distribution,
	assuming a Markov process.
	"""
	MAXITERS = 50
	# print 'Solve for pi:', p
	n = p.shape[0]
	assert p.shape == (n,n)
	pi = Num.ones((n,), Num.Float)/float(n)
	nxtnorm = None
	iter = 0
	npi = None
	while iter < MAXITERS:
		nxt = Num.matrixmultiply(pi, p)
		# print "pi*p=", nxt
		nxtnorm = Num.sum(nxt, axis=0)
		# print "nxtnorm=", nxtnorm
		npi = nxt / nxtnorm
		if Num.square(pi-npi).sum() < 1e-8:
			break
		pi = npi
		iter += 1
	if iter == MAXITERS:
		raise NoConvergenceError, (nxtnorm, Num.square(pi-npi).sum())
	if abs(nxtnorm-1) > 1e-3:
		raise NotMarkovError, nxtnorm
	return npi


def kl_nonzero_tr_probs(pp, qq):
	"""KL distance, given a matrix of nonzero transition probabilities.
	Each matrix indexes states as pp[from,to], and contains
	P(to given from) as a conditional probability,
	where for any from, the Sum over to( pp[from,to]) = 1.
	"""
	EPS = 1e-6
	pi = solve_for_pi(pp)
	# print "pi=", pi
	o = 0.0
	for (i, pi_i) in enumerate(pi):
		if pi_i > EPS:
			# These following two normalizations are formally
			# unnecessary.
			# print 'Nspp,qq=', Num.sum(pp[i,:]), Num.sum(qq[i,:])
			assert abs( Num.sum(pp[i,:]) - 1) < 1e-4
			assert abs( Num.sum(qq[i,:]) - 1) < 1e-4
			d = kl_nonzero_probs(pp[i,:], qq[i,:])
			# print 'i,d,pi=', i, d, pi_i
			o += d * pi_i
	return o


def kl_nonzero_tr_prob_m(pp, qq):
	assert len(pp.shape) == 2
	assert pp.shape == qq.shape
	EPS = 1e-6
	pi = solve_for_pi(pp)
	o = Num.zeros(pp.shape, Num.Float)
	for (i, pi_i) in enumerate(pi):
		if pi_i > EPS:
			pnext = pp[i,:]/Num.sum(pp[i,:])
			qnext = qq[i,:]/Num.sum(qq[i,:])
			d = kl_nonzero_prob_m(pnext, qnext) * pi_i
			Num.add(o[i], d, o[i])
	return o


def cross(a, b):
	o = []
	for aa in a:
		for ab in b:
			o.append( (aa,ab) )
	return o


def kldist_Markov(p, q, N=None):
	"""Kullback-Liebler distance between two matricies
	of bigram counts.
	"""

	p = Num.asarray(p, Num.Int)
	q = Num.asarray(q, Num.Int)
	assert p.shape == q.shape
	if N is None:
		N = p.shape[0]**2 * 30
	rN = int(round(math.sqrt(2*N)))
	pP = estimate_tr_probs(p, rN)
	# print 'pP=', pP
	qP = estimate_tr_probs(q, rN)
	# print 'qP=', qP
	o = []
	for (pp,qq) in random.sample(cross(pP,qP), N):
		# print "pp=", pp
		# print "qq=", qq
		o.append(kl_nonzero_tr_probs(pp, qq))
	avg, sigma = gpkavg.avg(o, None, 0.0001)
	return (avg, sigma)


def kldist_Markov_m(p, q, N=None):
	"""Kullback-Liebler distance between two matrices
	of bigram counts.
	"""

	p = Num.asarray(p, Num.Int)
	q = Num.asarray(q, Num.Int)
	assert p.shape == q.shape
	if N is None:
		N = p.shape[0]**2 * 30
	rN = int(round(math.sqrt(2*N)))
	pP = estimate_tr_probs(p, rN)
	# print 'pP=', pP
	qP = estimate_tr_probs(q, rN)
	# print 'qP=', qP
	n = p.shape[0]
	assert q.shape[0] == n
	o = Num.zeros((n,n), Num.Float)
	oo = []
	for (pp,qq) in random.sample(cross(pP,qP), N):
		# print 'pp,qq=', pp, qq
		tmp = kl_nonzero_tr_prob_m(pp, qq)
		# print 'tmp=', tmp
		o += tmp
		oo.append(kl_nonzero_tr_probs(pp, qq))
	avg, sigma = gpkavg.avg(oo, None, 0.0001)
	return (o/(n*n), avg, sigma)


def kldist_Markov_mm(*p):
	"""List of Kullback-Liebler distances between all combinations
	of pairs of matrices of bigram counts.
	It returns a list of matrices of all the distances.
	Each item on the list is a sample of the distance histogram.
	"""

	# ??? Darned if I know what "N" is.
	rN = int(round(math.sqrt(2*N)))
	pP = []
	n = None
	for pp in p:
		ppa = Num.asarray(p, Num.Int)
		if n is None:
			n = p.shape[0]
		assert p.shape[0] == n
		pP.append( estimate_tr_probs(ppa, rN) )

	samples = random.sample(cross(range(rN), range(rN)), N)
	o = []
	for (x,y) in samples:
		tmp = Num.zeros((len(p), len(p)), Num.Float)
		for (i, ppl) in enumerate(pP):
			for (j, qql) in enumerate(pP):
				tmp[i,j] = kl_nonzero_probs(ppl[x], qql[y])
		o.append( tmp )
	return o



if __name__ == '__main__':
	# print kldist_vec([100,100], [1,100])
	print kldist_Markov(
		[[0,0,10],[0,0,10],[0,0,10]],
		[[20,0,0],[0,20,0],[0,0,20]]
		)
