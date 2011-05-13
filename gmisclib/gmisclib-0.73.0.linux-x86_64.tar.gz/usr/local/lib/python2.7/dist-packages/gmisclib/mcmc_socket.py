# -*- coding: utf-8 -*-
"""This is a helper module to make use of mcmc.py and mcmc_big.py.
It allows you to conveniently run a Monte-Carlo simulation of any
kind until it converges (L{stepper.run_to_bottom}) or until it
has explored a large chunk of parameter space (L{stepper.run_to_ergodic}).

It also helps you with logging the process.

When run in parallel, each processor does its thing more-or-less
independently.   However, every few steps, they exchange notes on
their current progress.   If one finds an improved vertex, it will be
passed on to other processors via mcmc_cooperate.py.
"""

import sys
import random
import numpy

import die
import mcmc
import mcmc_helper as MCH
Debug = 0
from mcmc_helper import TooManyLoops, warnevery, logger_template, test
from mcmc_helper import step_acceptor, make_stepper_from_lov

import mcmc_cooperate as MC



class stepper(MCH.stepper):
	def __init__(self, x, maxloops=-1, logger=None, share=None):
		assert maxloops == -1
		MCH.stepper.__init__(self, x, maxloops, logger)
		self.comm = MC.connection(*share)
		self.barrier = MC.Barrier(0)
		self.delta_b = MC.Barrier(1)
		die.info('# mpi stepper rank=%d size=%d' % (self.rank(), self.size()))


	def reset_loops(self, maxloops=-1):
		assert maxloops == -1
		MCH.stepper.reset_loops(self, maxloops)


	def communicate_hook(self, id):
		self.note('chook iter=%d' % self.iter, 4)
		self.note('chook active iter=%d' % self.iter, 3)
		c = self.x.current()
		v = c.vec()
		lp = c.logp()
		nlp, nv = self.comm.swap_vec(lp, v)
		delta = nlp - lp
		if self.x.acceptable(delta):
			q = self.x._set_current(c.new(nv-v, logp=nlp))
			self.note('communicate accepted: %s' % q, 1)
		else:
			self.note('communicate not accepted %g vs %g' % (nlp, lp), 1)
			self.x._set_current(self.x.current())
		sys.stdout.flush()


	def _nc_get_hook(self, nc):
		rv = self.comm.get_consensus('nc', nc, self.barrier, "float_median")
		self.barrier += self.delta_b
		return rv

	def _not_at_bottom(self, xchanged, nchg, es, dotchanged, ndot):
		mytmp = (numpy.sometrue(numpy.less(xchanged,nchg))
					or es<1.0 or dotchanged<ndot
					or self.x.acceptable.T()>1.5
				)
		rv = self.comm.get_consensus('nc', mytmp, self.barrier, "float_median")
		self.barrier += self.delta_b
		return rv > 0.25


	def synchronize_start(self, id):
		self.comm.barrier(self.barrier.deepen(1))

	def synchronize_end(self, id):
		self.comm.barrier(self.barrier.deepen(2))
		self.barrier += self.delta_b


	def synchronize_abort(self, id):
                self.comm.barrier(self.barrier.deepen(100))
                self.barrier += self.delta_b


	def note(self, s, lvl):
		if Debug >= lvl:
			sys.stderr.writelines('# %s, rank=%d\n' % (s, self.comm.rank()))
			sys.stderr.flush()
	
	
	def close(self):
	    self.comm.close()
	    MCH.stepper.close(self)

	def size(self):
		return self.comm.rank()[0]

	def rank(self):
		return self.comm.rank()[1]


def precompute_logp(lop):
	raise RuntimeError, "Not Implemented"


def test(args):
	def test_logp(x, c):
		# print '#', x[0], x[1]
		return -(x[0]-x[1]**2)**2 + 0.001*x[1]**2
	x = mcmc.bootstepper(test_logp, numpy.array([0.0,2.0]),
				numpy.array([[1.0,0],[0,2.0]]))
	# print 'TEST: rank=', rank()
	thr = stepper(x, share=args)
	# nsteps = thr.run_to_bottom(x)
	# print '#nsteps', nsteps
	# assert nsteps < 100
	for i in range(20):
		print 'RTC'
		thr.run_to_change(2)
		print 'RTE'
		thr.run_to_ergodic(1.0)
		print 'DONE'
	thr.close()



if __name__ == '__main__':
	test(MC.test_args)
