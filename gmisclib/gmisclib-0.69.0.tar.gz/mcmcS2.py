
"""Markov-Chain Monte-Carlo algorithms.

Here, we do MCMC when -log(p) is a sum of squares."""

import mcmcSQ
import die

import mcmc
import g_implements
import findleak

_s = None

def go_step(x, showvec):
	global _s

	findleak.vm('go_step start')
	assert g_implements.impl(x.current(), mcmc.position_base), "Bad pseudoposition: %s" % g_implements.why(x.current(), mcmc.position_base)
	if _s is None:
		print "INITIALIZING mcmc"
		_s = mcmc.bootstepper(None, x.current(), x.archive.mvn.cov, None)
		findleak.vm('go_step initialize end')
	print "SQ STEP"
	accepted = x.step(showvec=showvec, atmisc={'stepper': 'SQ'})
	findleak.vm('go_step accepted start')
	if accepted:
		cur = x.current()
		print 'Cur from SQ:', cur.prms()
		_s._set_current( cur )
		findleak.vm('go_step accepted end')
	findleak.vm('go_step Bootstep start')
	if(len(_s.archive) > _s.np/_s.F):
		print "BOOT STEP"
		accepted = _s.step()
		print 'Accepted:', accepted
		cur = x.current()
		print 'Cur from BOOT:', cur.prms()
		SQpos = _s.current()
		assert isinstance(SQpos, mcmcSQ.position)
		x.archive.add( SQpos )
		if accepted:
			findleak.vm('go_step BOOTstep-set_current start')
			x._set_current( SQpos )
			findleak.vm('go_step BOOTstep-set_current end')
		x.print_at( misc = {'stepper': 'Boot', 'BootScale': _s.a[0].vs()} )
		findleak.vm('go_step BOOTstep end')
	#findleak.print_top_N(20)
	findleak.vm('go_step end')

mcmcSQ.go_step = go_step





if __name__ == '__main__':
	import sys
	if len(sys.argv) <= 1:
		print __doc__
		die.exit(0)
	mcmcSQ.go(sys.argv)
