
"""This returns the entropy of a probability distribution that
produced a given sample.
"""

import Num
import mcmc
import mcmc_helper
import gpkavg
import math

import kl_dist


def entropy_probs(p):
	"""Entropy of a probability distribution."""
	rv = Num.sum( p*Num.log(p) ) / math.log(2)
	return rv


def entropy_vec(p, N=None, F=1.0, Clip=0.01):
	"""Entropy of a frequency distribution p.
	Here, we assume that p is counts
	derived from multinomial distributed data;
	they are not normalized to one.
	"""

	p = Num.asarray(p, Num.Int)
	if N is None:
		N = p.shape[0]**2 * 30
	assert Num.sum(p) > 0
	pstart = ((0.5+p)/Num.sum(0.5+p))
	pV = 0.1*Num.identity(p.shape[0])/float(p.shape[0])**1.5
	xp = mcmc.bootstepper(kl_dist.multinomial_logp, pstart, pV,
				c=(p,F), fixer=kl_dist.multinomial_fixer)
	mcmch = mcmc_helper.stepper(xp)
	mcmch.run_to_bottom()
	mcmch.run_to_ergodic(5.0)
	o = []
	while len(o) < N:
		mcmch.run_to_ergodic(1.0/math.sqrt(N))
		o.append( entropy_probs( kl_dist.P(xp.prms()) ) )
	avg, sigma = gpkavg.avg(o, None, Clip)
	return (-avg, sigma)



if __name__ == '__main__':
	print entropy_vec([100,100,100.0,100.0])
