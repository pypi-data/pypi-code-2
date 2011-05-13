"""This is a helper module to make use of mcmc.py and mcmc_big.py.
It allows you to conveniently run a Monte-Carlo simulation of any
kind until it converges (L{stepper.run_to_bottom}) or until it
has explored a large chunk of parameter space (L{stepper.run_to_ergodic}).

It also helps you with logging the process.

When run in parallel, each processor does its thing more-or-less
independently.   However, every few steps, they exchange notes on
their current progress.   If one finds an improved vertex, it will be
passed on to other processors via MPI.

Tested with mpi4py version 1.1.0, http://mpi4py.scipy.org
"""

import sys
from mpi4py import MPI	# This uses mpi4py
import random
import numpy
from gmisclib import die
from gmisclib import mcmc
from gmisclib import mcmc_helper as MCH
Debug = 0
from gmisclib.mcmc_helper import TooManyLoops, warnevery, logger_template, test
from gmisclib.mcmc_helper import step_acceptor, make_stepper_from_lov

mpi = MPI.COMM_WORLD




class stepper(MCH.stepper):
	def __init__(self, x, maxloops=-1, logger=None):
		die.info('# mpi stepper rank=%d size=%d' % (rank(), size()))
		assert maxloops == -1
		self.maxloops = -1
		MCH.stepper.__init__(self, x, maxloops, logger)


	def reset_loops(self, maxloops=-1):
		assert maxloops == -1
		self.maxloops = -1


	def communicate_hook(self, id):
		self.note('chook iter=%d' % self.iter, 4)
		if size() > 1:
			self.note('chook active iter=%d' % self.iter, 3)
			c = self.x.current()
			v = c.vec()
			lp = c.logp()

			r = rank()
			s = size()
			self.note('sendrecv from %d to %d' % (r, (r+1)%s), 5)
			nv, nlp, nid = mpi.sendrecv(sendobj=(v, lp, id),
								dest=(r+1)%s, sendtag=self.MPIID,
								source=(r+s-1)%s,
								recvtag=self.MPIID
								)

			self.note('communicate succeeded from %s' % nid, 1)
			delta = nlp - lp
			if self.x.acceptable(delta):
				q = self.x._set_current(c.new(nv-v, logp=nlp))
				self.note('communicate accepted: %s' % q, 1)
			else:
				self.note('communicate not accepted %g vs %g' % (nlp, lp), 1)
				self.x._set_current(self.x.current())
			sys.stdout.flush()


	MPIID = 1241

	# def _not_enough_changes(self, n, ncw):
		# mytmp = n < ncw
		# self.note('_nyc pre')
		# ntrue = mpi.allreduce(int(mytmp), MPI.SUM)
		# self.note('_nyc post')
		# return ntrue*3 >= size()


	def _nc_get_hook(self, nc):
		self.note('_nye pre', 5)
		ncsum = mpi.allreduce(float(nc), MPI.SUM)
		self.note('_nye post', 5)
		return ncsum/float(size())


	def _not_at_bottom(self, xchanged, nchg, es, dotchanged, ndot):
		mytmp = (numpy.sometrue(numpy.less(xchanged,nchg))
					or es<1.0 or dotchanged<ndot
					or self.x.acceptable.T()>1.5
				)
		self.note('_nab pre', 5)
		ntrue = mpi.allreduce(int(mytmp), MPI.SUM)
		self.note('_nab post', 5)
		return ntrue*4 >= size()


	def join(self, id):
		self.note('pre join %s' % id, 5)
		rootid = mpi.bcast(id)
		assert rootid == id
		self.note('post join %s' % id, 5)


	def note(self, s, lvl):
		if Debug >= lvl:
			sys.stderr.writelines('# %s, rank=%d\n' % (s, rank()))
			sys.stderr.flush()


def precompute_logp(lop):
	"""Does a parallel evaluation of logp for all items in lop.
	"""
	nper = len(lop)//size()
	r = rank()
	mychunk = lop[r*nper:(r+1)*nper]
	for p in mychunk:
		q = p.logp()
		print 'logp=', q, 'for rank', r
	for r in range(size()):
		nc = mpi.bcast(mychunk, r)
		lop[r*nper:(r+1)*nper] = nc
	mpi.barrier()


def is_root():
	return mpi.Get_rank() == 0

def size():
	return mpi.Get_size()

def rank():
	return mpi.Get_rank()


def test():
	def test_logp(x, c):
		# print '#', x[0], x[1]
		return -(x[0]-x[1]**2)**2 + 0.001*x[1]**2
	x = mcmc.bootstepper(test_logp, numpy.array([0.0,2.0]),
				numpy.array([[1.0,0],[0,2.0]]))
	print 'TEST: rank=', rank()
	thr = stepper(x)
	# nsteps = thr.run_to_bottom(x)
	# print '#nsteps', nsteps
	# assert nsteps < 100
	for i in range(2):
		print 'RTC'
		thr.run_to_change(2)
		print 'RTE'
		thr.run_to_ergodic(1.0)
		print 'DONE'
	thr.close()



if __name__ == '__main__':
	test()
