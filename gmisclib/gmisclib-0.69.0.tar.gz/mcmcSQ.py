
"""Markov-Chain Monte-Carlo algorithms.

Here, we do MCMC when -log(p) is a sum of squares."""


import sys
import math
import random
import Num
import RandomArray
import LinearAlgebra
import g_localfit
import avio
import time
import multivariate_normal
import gpkmisc
import die
import g_implements
from mcmc import _read, _start_is_list_a, def_logger, stepper


# These fudge factors are approximately correct so that,
# for a multivariate Gaussian distribution, you will
# get the same answer with minimize=1 as with minimize=0.
# Minimize=0 -> Markov Chain Monte Carlo.
VARFUDGE = 0.707
VF2 = 1.2
EFUDGE = 1.0/2.0
WORRY = 6
MINIMIZE = 0.0
D = 1

__version__ = "$Revision: 1.62 $"


class CantGetPoint(RuntimeError):
	def __init__(self, s):
		RuntimeError.__init__(self, s)

class DontGoHere(ValueError):
	def __init__(self, s):
		ValueError.__init__(self, s)


class NegativeEigenvalue(ValueError):
	def __init__(self, ev):
		ValueError.__init__(self, str(ev))
		self.ev = ev



class BadlyConditioned(RuntimeError):
	def __init__(self, s):
		RuntimeError.__init__(self, s)



class timer:
	def __init__(self):
		self.tot = 0.0
		self.t0 = None
		self.nc = 1.0
	
	def start(self):
		assert self.t0 is None
		self.t0 = time.time()
	
	def stop(self):
		assert self.t0 is not None
		delta = time.time() - self.t0
		assert delta >= 0.0
		self.tot += delta
		self.t0 = None
		self.nc += 1

	def is_running(self):
		return self.t0 is not None

	def running_total(self):
		if self.t0 is not None:
			t = time.time()
			self.tot += t-self.t0
			self.t0 = t
		return self.tot

	def get(self):
		t = self.running_total()
		nc = self.nc + 0.5*self.is_running()
		return t/nc

	def leak(self, fac=0.8):
		self.tot *= fac
		self.nc *= fac


class problem_definition(object):
	@g_implements.make_optional
	@g_implements.make_varargs
	def __init__(self, resid_fcn, c, fixer=None):
		self.c = c
		self._fixer = fixer
		assert callable(resid_fcn)
		self.rf = resid_fcn

	def resid(self, x):
		return (self.rf)(x, self.c)

	def fixer(self, x):
		"""This allows for symmetries in problems."""
		if self._fixer is not None:
			return (self._fixer)(x, self.c)
		return x


class position(object):
	HUGE = 1e30

	@g_implements.make_optional
	def __init__(self, x, problem_def, resid=None):
		g_implements.check(problem_def, problem_definition)
		self.pd = problem_def
		# print "position:x=", x
		self.x = self.pd.fixer(Num.array(x, Num.Float, copy=True))
		assert len(self.x.shape) == 1
		# print "self.x=", self.x
		# self.shape = self.x.shape
		self._r = resid
		self._ssq = None
		self.tmr = None


	def attach_timer(self, tmr):
		self.tmr = tmr



	def resid(self):
		if self._r is None:
			if self.tmr is not None:
				self.tmr.start()
			try:
				fv = self.pd.resid(self.x)
			except DontGoHere, x:
				print "Don't go here", x
				self._r = x
			else:
				if fv is None:
					print 'FV=none'
					self._r = DontGoHere( 'Function returned "None"' )
				else:
					print 'r=', fv
					self._r = Num.asarray(fv, Num.Float)
			if self.tmr is not None:
				self.tmr.stop()

		if isinstance(self._r, DontGoHere):
			if D:
				print 'position: DontGoHere'
				sys.stdout.flush()
			raise self._r
		return self._r



	def badspot(self):
		try:
			self.resid()
		except DontGoHere:
			return 1
		return 0


	def sumsq(self):
		if self._ssq is None:
			# print 'Computing sumsq' 
			try:
				tmp = self.resid()
			except DontGoHere:
				self._ssq = self.HUGE
			else:
				print 'tmp=', tmp
				self._ssq = Num.sum(tmp**2)
				if self._ssq > self._r.shape[0] * 1000.0:
					ri = Num.argsort(self._r)
					print '#WARN: Huge ssq:', ri[-1], ri[0], self._r.shape[0], self._r[ri[-1]], self._r[ri[0]]
		return self._ssq


	def logp(self):
		return -self.sumsq()/2.0

	def shape(self):
		return self.x.shape[0]

	def new(self, shift):
		"""Returns a new position, shifted by the specified amount."""
		tmp = position(self.x + shift, self.pd)
		tmp.attach_timer( self.tmr )
		return tmp

	def prms(self):
		return self.x

	def __str__(self):
		return '<POS %s -> %s>' % (str(self.x), str(self._logp))


def linear_least_squares_lambda(a, b, lmbda):
	assert len(a.shape) == 2
	assert len(b.shape) in (1, 2)
	ata = Num.matrixmultiply(Num.transpose(a), a)
	# print 'ata=', ata
	i = Num.identity(ata.shape[0])
	atb = Num.matrixmultiply(Num.transpose(a), b)
	atal = ata + i*lmbda
	ev_ata = LinearAlgebra.Heigenvalues(ata)
	ata = None	# Reclaim memory.
	ev_atal = ev_ata + lmbda	# Eigenvalues of atal
	if not Num.alltrue(ev_atal > 0.0):
		raise NegativeEigenvalue, min(ev_atal)
	x = -LinearAlgebra.solve_linear_equations(atal, atb)
	# print 'a=', a
	# print 'x=', x
	# print 'b=', b
	# print 'ax=', Num.matrixmultiply(a, x)
	# print 'ax+b', Num.matrixmultiply(a, x) + b
	# print '(ax+b)**2', (Num.matrixmultiply(a, x) + b)**2
	fiterr = Num.sum( (Num.matrixmultiply(a, x) + b)**2 )
	a = None	# Reclaim memory
	return (x, fiterr, atal, ev_ata)



def test_llsl_1():
	"""Simplest case - one parameter, one observation."""
	b0 = Num.array( (1,) )
	a0 = Num.array( ((1,),) )
	step, fiterr, atal, ev_ata = linear_least_squares_lambda(a0, b0, 0.0)
	# print step
	# print fiterr
	# print atal
	assert fiterr < 1e-6
	assert Num.alltrue(Num.absolute(step+1)<1e-6)

def test_llsl_1o():
	"""Overdetermined."""
	b0 = Num.array( (1,0) )
	a0 = Num.array( ((1,),(1,),) )
	step, fiterr, atal, ev_ata = linear_least_squares_lambda(a0, b0, 0.0)
	# print step
	# print fiterr
	# print atal
	assert abs(fiterr-0.5) < 1e-6
	assert Num.alltrue(Num.absolute(step+0.5)<1e-6)


def test_llsl_2u():
	"""Underdetermined."""
	b0 = Num.array((1,))
	a0 = Num.array(((1,1),))
	e = 0
	try:
		step, fiterr, atal, ev_ata = linear_least_squares_lambda(a0, b0, 0.0)
	except LinearAlgebra.LinAlgError, x:
		if str(x) == 'Singular matrix':
			e = 1
	assert e == 1, 'Should throw exception.'

	step, fiterr, atal, ev_ata = linear_least_squares_lambda(a0, b0, 1.0)
	# print step
	# print fiterr
	# print atal
	assert abs(step[0]-step[1]) < 0.01
	assert Num.sum(Num.ravel(step)**2) < 0.5
	assert fiterr < 0.5 and fiterr>0.01

	step, fiterr, atal, ev_ata = linear_least_squares_lambda(a0, b0, 0.0001)
	# print step
	# print fiterr
	# print atal
	assert abs(step[0]-step[1]) < 0.01
	assert abs(step[0]+step[1]+1) < 0.01
	assert fiterr < 0.001


def test_llsl_2():
	"""Simplest case - two parameters, two observations."""
	b0 = Num.array( (1,-1) )
	a0 = Num.array( ((1,1),(1,-1)) )
	step, fiterr, atal, ev_ata = linear_least_squares_lambda(a0, b0, 0.0)
	# print step
	# print fiterr
	# print atal
	assert fiterr < 1e-6
	assert Num.sum(Num.absolute(step-[0,-1]))<1e-6


	

SINGPASSES = 10

class Lambda_c:
	__doc__ = """This class remembers and increments Lambda,
	for a Levenberg-Marquart-like algorithm.  Initially, when
	we're trying to find the first acceptable step, the adjustments
	to lambda are large.   Then, once a couple of acceptable
	steps have been found, we make the adjustments to lambda
	smaller and also begin to enforce the optimal ratio of
	accepted steps to rejected steps (1:3).
	Later, we keep enforcing the ratio, and make the adjustments
	to lambda still smaller.
	"""

	EARLY_REJECT = 10.0
	EARLY_ACCEPT = 0.1
	ACCEPT = 0.2
	LATE_ACCEPT = 0.6
	AR_RATIO = 0.25	# If everything is going well, we'd like to accept 25% of the steps.
	MIN = 1e-10
	NEG = 5.0
	SING = 2.0
	LIM_F = 10.0

	def __init__(self, lmbda, np):
		"""lmbda is the initial value;
		np is the number of parameters, which is used to control
		whether adjustments are fine (late) or coarse (early).
		"""
		self._lmbda = lmbda
		self.nacc = 0
		self.np = np
		self.fbek = 1.0
		self.vfac = 1.0

	def adjust_BadEstKluge(self, f):
		self.fbek = 1.0/math.hypot(1.0, f)

	def adjust_VfacKluge(self, vfac):
		self.vfac = vfac

	def fa(self):
		# Npf is the result of a complicated calculation.
		# The question is :
		# Assume that you are simulated annealing, and are in the equilibrium
		# distribution for a quadratic np-dimensional potential.
		# Assume you are stepping with a multivariate gaussian step given
		# by that same potential.  What is the probability that the
		# attempted step will bring you closer to the center (lower the E)?
		# It's 50% for a 1-D distribution, but gets smaller for higher D,
		# asymptotically reaching a constant.  The logic is that along
		# a selected direction, you step closer half of the time,
		# but, you're also stepping sideways, and the sideways part of the
		# step can increase the distance.
		tmp = self.vfac * float(self.np-1)/(1.0 + self.np)
		npf = math.exp(-tmp**2)

		return math.sqrt(self.fbek) * npf

	def fr(self):
		return self.fbek

	def lmbda(self):
		"""Return the current value of lambda."""
		return self._lmbda

	def neg(self, min_eigenval):
		self._lmbda = max(self._lmbda*self.NEG, -1.5*min_eigenval)

	def sing(self):
		self._lmbda *= self.SING

	def accept(self):
		if self.nacc < 2:
			f = self.EARLY_ACCEPT ** self.fa()
		elif self.nacc > self.np:
			f = self.LATE_ACCEPT ** self.fa()
		else:
			f = self.ACCEPT ** self.fa()
		self._lmbda = max(f*self._lmbda, self.MIN)
		self.nacc += 1


	def reject(self):
		if self.nacc < 2:
			f = self.EARLY_REJECT ** self.fr()
		elif self.nacc > self.np:
			f = self.LATE_ACCEPT ** (-self.AR_RATIO * self.fr())
		else:
			f = self.ACCEPT ** (-self.AR_RATIO * self.fr())
		self._lmbda *= f


	def low_lim(self, x):
		x /= self.LIM_F
		if self._lmbda < x:
			if D:
				print 'Lambda limited to smallest ev: %g -> %g' % (self._lmbda, x)
			self._lmbda = x


	def high_lim(self, x):
		x *= self.LIM_F
		if self._lmbda > x:
			if D:
				print 'Lambda limited to largest ev: %g -> %g' % (self._lmbda, x)
			self._lmbda = x


def _evec_write(log_fd, a_vec, a_val, note):
	Nlim = 500
	o = ['note=%s' % note,  'eigenvalue=%g' % a_val]
	# XXX Below error checks shouldn't be needed...
	try:
		sq = Num.absolute(a_vec)**2
	except OverflowError:
		die.info("note=" + note)
		die.info("a=" + str(a_vec))
		raise
	idx = Num.argsort(sq)
	total = Num.sum(sq)
	ssq = 0.0
	n = 0
	for i in range(idx.shape[0]-1, -1, -1):
		j = idx[i]
		o.append( 'c%d=%.3f' % (j, a_vec[j]))
		ssq += sq[j]
		n += 1
		if ssq > total*(1-n/float(Nlim)):
			break
	log_fd.write('#Evec: ' + '; '.join(o) + '\n')
	log_fd.flush()



class SQstepper(stepper):
	def __init__(self, pd, lop, v, minimize=0):
		stepper.__init__(self, pd, v)
		assert check_list_of_positions(lop, pd)
		self.archive = lop
		self.np = self.current().shape()
		self.fcntime = timer()
		self.runtime = timer()

		self.lmbda = Lambda_c(1e-6, np)
		self.np = np
		self.archive = archiver(np, v, pd, self.fcntime)

		ZZZ
		for p in positions:
			p.tmr = self.fcntime
			if self.archive.add_initial( p ):
				break

		ZZZ
		for x in locations:
			if self.archive.add_initial( position(x, pd, tmr=self.fcntime) ):
				break
		self.archive.go()
		self.minimize = minimize
		self.logfd = None
		self.a = None
		self.b = None


	def sumsq(self):
		return self.current().sumsq()


	def _set_current(self, newcurrent):
		self.archive.set_current(newcurrent)
		if self.needs_a_reset():
			self.reset()


	def current(self):
		return self.archive.current()

	def last(self):
		return self.archive.last()


	def _step_ab(self, a, b):
		# print 'A', a
		# print 'B', b
		ipass = 0
		while ipass < SINGPASSES:
			print 'PASS', ipass, 'lambda', self.lmbda.lmbda()
			try:
				step, fiterr, atal, ev_ata = linear_least_squares_lambda(a, b, self.lmbda.lmbda())
			except LinearAlgebra.LinAlgError, x:
				if x.startswith('Singular'):
					die.warn('Singular equations in _step_ab(). Lambda=%g' % self.lmbda.lmbda())
					self.lmbda.sing()
				else:
					raise
			except NegativeEigenvalue, x:
				die.warn('Negative eigenvalue in llsql. Lambda=%g, ev=%g'
						% (self.lmbda.lmbda(), x.ev))
				self.lmbda.neg(x.ev)
			else:
				self.lmbda.low_lim( min(ev_ata) )
				self.lmbda.high_lim( max(ev_ata) )
				break
			ipass += 1
		if ipass >= SINGPASSES:
			raise BadlyConditioned, "Can't get positive eigenvalues: pass=%d lambda=%g" % (ipass, self.lmbda.lmbda())
		here = self.current()
		print 'HERE', here.prms()
		print 'STEP', step

		ctr = here.prms() + step
		print 'CTR', ctr
		sfac = self.minimize
		vfac = (VARFUDGE + (VF2-VARFUDGE)*self.minimize)**2
		self.lmbda.adjust_VfacKluge(vfac)
		print 'sfac=', sfac, 'vfac=', vfac
		return self._trysteps(here.prms() + sfac*step, vfac*LinearAlgebra.inverse(atal), here)


	def _trysteps(self, ctr, var, here):
		MAXTRIES = 10
		mvn = multivariate_normal.multivariate_normal(ctr, var)
		i = 0
		print 'fcntime=', self.fcntime.get(), self.runtime.get()
		while i == 0 or (i < MAXTRIES and 2*self.fcntime.get() < self.runtime.get()):
			newx = mvn.sample()
			print 'NEWX', newx
			sys.stdout.flush()
			accepted = self.trypos(newx, here)
			if accepted:
				if i == 0:
					self.lmbda.accept()
				break
			else:
				if i == 0:
					self.lmbda.reject()
			i += 1
		print 'Accepted:', accepted
		sys.stdout.flush()
		return accepted


	def trypos(self, newx, here):
		print 'NEWX', newx
		sys.stdout.flush()
		new = position(newx, here.pd)
		new.attach_timer(self.fcntime)
		print 'NEWLOGP', new.logp(), here.logp()
		if new.logp() > here.logp()-random.expovariate(EFUDGE/(EFUDGE+self.minimize)):
			self._set_current( new )
			self._set_failed( None )
			accepted = 1
		else:
			self._set_failed( new )
			accepted = 0
		self.archive.add( new )
		return accepted


	def step(self, evmisc=None, atmisc=None, showvec=0):
		"""Returns 0 or 1, depending on whether the step was accepted or not.
		"""
		SQstepper.step(self)
		if evmisc is None:
			evmisc = {}
		if atmisc is None:
			atmisc = {}
		self.runtime.start()
		self.b, self.a, not_locally_linear = get_localfit(self.archive)
		self.lmbda.adjust_BadEstKluge(not_locally_linear)
		o = self._step_ab(self.a, self.b)
		self.print_at(misc=atmisc)
		self.print_ev_diag(misc=evmisc, vectors=showvec)
		self.fcntime.leak()
		self.runtime.stop()
		self.runtime.leak()

		# Just save some memory here:
		self.archive.trim_initial()
		return o

	def status(self):
		o = ['E=%g' % self.sumsq(),
			'fcntime=%s' % self.fcntime.get(),
			'runtime=%s' % self.runtime.get(),
			'lambda=%s' % self.lmbda.lmbda()
			]
		return '; '.join(o) + ';'


	def print_ev_diag(self, misc=None, vectors=0):
		if misc is None:
			misc = {}
		if self.logfd is None:
			return
		log_fd = self.logfd
		curv = Num.matrixmultiply(Num.transpose(self.a), self.a)
	
		if vectors:
			eval, evec = LinearAlgebra.Heigenvectors(curv)
		else:
			eval = LinearAlgebra.Heigenvalues(curv)
			evec = None
	
		mx_e = gpkmisc.N_maximum(eval)
		o = misc.copy()
		o['Max_EV'] = '%6g' % mx_e
		o['Min_EV'] = '%6g' % gpkmisc.N_minimum(eval)
		lg_thr = mx_e/10.0
		sm_thr = mx_e/1e4
		o['N_large_ev'] = Num.sum(Num.greater(eval, lg_thr))
		o['large_thr'] = '%6g' % lg_thr
		o['N_small_ev'] = Num.sum(Num.less(eval, sm_thr))
		o['small_thr'] = '%6g' % sm_thr
		o['Median_EV'] = '%6g' % gpkmisc.N_median(eval)
		o['N_sm_lambda'] = Num.sum(Num.less(eval, self.lmbda.lmbda()))
		o['lambda'] = '%6g' % self.lmbda.lmbda()
		log_fd.write('#EV: ' + avio.concoct(o) + '\n')
		if vectors:
			n = eval.shape[0]
			_evec_write(log_fd, evec[0,:], eval[0], "S")
			if n > 2:
				_evec_write(log_fd, evec[1,:], eval[1], "S")
			if n > 1:
				_evec_write(log_fd, evec[-1,:], eval[-1], "L")
			if n > 3:
				_evec_write(log_fd, evec[-2,:], eval[-2], "L")
		log_fd.flush()


	def print_at(self, misc=None):
		"""Prints a file to match the old C++ optimizer output."""
		if misc is None:
			misc = {}
		if self.logfd is None:
			return
		log_fd = self.logfd
		if self.last() is not None:
			log_fd.write("#move:")
			curr = self.current()
			p_step = curr.prms() - self.last().prms()
			for i in range(p_step.shape[0]):
				log_fd.write(" %6g" % p_step[i])
			log_fd.write('\n')
		log_fd.write('# ' + self.status() + avio.concoct(misc) + '\n')
		log_fd.write('#D: ' + self.archive.describe() + '\n')
		currp = self.current().prms()
		for i in range(self.np):
			log_fd.write(" %g" % currp[i])
		log_fd.write('\n')
		log_fd.flush()
	

	def print_rejected(self, r, misc=None):
		if misc is None:
			misc = {}
		if self.logfd is None:
			return
		log_fd = self.logfd
		o = misc.copy()
		o['E'] = r.sumsq()
		o['lambda'] = self.lmbda.lmbda()
		log_fd.write('#R ' + avio.concoct(o) + '\n')
		log_fd.write('#r: ')
		rp = r.prms()
		for i in range(self.np):
			log_fd.write(" %g" % rp[i])
		log_fd.write('\n')
		log_fd.flush()
	


def test_stepper():
	def _tgf_fn(p, c):
		return p*(10.0, 0.3)

	NH = 100
	ND = 2
	c = None
	p = []
	for i in range(NH):
		p.append( RandomArray.multivariate_normal(Num.zeros((ND,)), Num.identity(ND)) )
	s = SQstepper( _tgf_fn, ND, c, Num.identity(ND, Num.Float),
			locations=p,
			minimize=1
			)
	s.logfd = open("/tmp/foo.log", "w")

	sx = 0.0
	sy = 0.0
	sxx = 0.0
	syy = 0.0
	sxy = 0.0
	NS = 3000
	for i in range(NS):
		acc = s.step()
		cur = s.current()
		cx = cur.prms()
		print 'Q', i, cx[0], cx[1], acc, s.lmbda.lmbda()
		sx += cx[0]
		sy += cx[1]
		sxx += cx[0]*cx[0]
		syy += cx[1]*cx[1]
		sxy += cx[0]*cx[1]
	print sx/NS, sy/NS, sxx/NS, syy/NS, sxy/NS
	assert abs(sx) < 10*math.sqrt(NS)
	assert abs(sy) < 10*math.sqrt(NS)





class archiver:
	__doc__ = """
		This class stores history information on the optimization.
		It's main output is from the routine choose(), which selects
		a set of points from the history from which g_localfit can
		compute the Jacobian matrix.
		"""
	SMALL_VOL = 0.1
	SMALL_PRE = 0.5

	def __init__(self, np, v, pd, fcntime):
		self.np = np
		self.ntake = np+2
		self.history = []
		self.initial = []
		assert isinstance(pd, problem_definition)
		self.pd = pd
		self.deriv_pass = None
		self.na_used = None
		self.ni_used = None
		self.nn_used = None
		self.na_unused = None
		self.newscale = 1.0
		self.description = []
		self.mvn = multivariate_normal.multivariate_normal(Num.zeros((np,), Num.Float), v)
		self.fcntime = fcntime
		self._current = None
		self._last = None


	def trim_initial(self, steps):
		efflen = len(self.history) + len(self.initial)/4
		if efflen > 2*self.np:
			ilen = (2*self.np - len(self.history)) * 4
			if ilen > 0  and  ilen < len(self.initial):
				self.initial[: -ilen] = []
			elif ilen <= 0:
				self.initial = []


	def get_new(self):
		if D:
			print "GET_NEW:", self.newscale
		tries = 0
		x = random.choice(self.history[-self.np:])
		while tries < 50:
			step = self.mvn.sample() * self.newscale
			np = position(x.prms() + step, self.pd)
			np.attach_timer(self.fcntime)
			if D:
				print 'GET ANOTHER:', np.prms()

			if not np.badspot():
				break
			if D:
				print 'BAD SPOT'
		if np.badspot():
			die.info("Quite possibly v is set incorrectly.")
			die.warn("Can't get a new point: failed after %d tries" % tries)
			raise CantGetPoint, ''

		# Let's have a little more than normal freedom here...
		# Arrange to have these points scattered a little more widely
		# than the MCMC distribution.
		if np.logp() > x.logp()-random.expovariate(0.3):
			self.newscale = min(1.5*self.newscale, 1000.0)
		else:
			self.newscale = max(0.7*self.newscale, 0.01)

		sys.stdout.flush()
		return np


	def widen(self):
		self.ntake += 1


	def narrow(self):
		if self.ntake > self.np+1:
			self.ntake -= 1


	def choose_guts(self):
		if D: print "CHOOSE_GUTS"
		current = self.current()
		o = []
		nt = 0.0
		self.na_used = 0
		self.nn_used = 0
		self.ni_used = 0
		self.na_unused = 0
		self.description = []

		# Occasionally add one completely new observation.
		# The intent here is to make sure the set of observations
		# doesn't collapse into a subspace.
		try:
			if nt < self.ntake and random.random()<1.0/math.sqrt(self.np):
				anp = self.get_new()
				self.add(anp)
				o.append( (anp.prms()-current.prms(), anp.resid()) )
				self.description.append('N%.1e' % self.newscale)
				self.nn_used += 1
				nt += 1.0
		except CantGetPoint:
			pass

		# Explicitly put in the current position.
		# If/when it appears in the list, it will get dropped as too close.
		o.append( (current.prms()-current.prms(), current.resid()) )
		nt += 1

		# We want the end of the history:
		score1 = Num.arrayrange(len(self.history))
		logp = Num.array( [ x.logp() for x in self.history ] )
		# We want big logp, but small differences amongst the values
		# of logp are unimportant:
		score2 = Num.argsort( logp + RandomArray.chi_square(1, logp.shape))
		# We will randomly push a few points to the end of the list,
		# just to make sure we're not always using the same data.
		score3 = RandomArray.expovariate(2.0/float(len(self.ntake)), logp.shape)
		score = score2 + score1 + score3
		ordering = Num.argsort(score)

		i = len(self.history) - 1
		# Use the recent observations:
		while nt<self.ntake and i >= 0:
			shi = self.history[ordering[i]]

			# The factor is np, instead of t[1].shape[0], because
			# the sample points all sit in a self.np -dimensional
			# subspace.
			dclose = self.SMALL_PRE*self.np*(self.SMALL_VOL/max(self.ntake, len(o)))**(2.0/self.np)
			closest = 1e30
			for t in o:
				# We don't want points that are too similar to points
				# that we have already chosen.   The dependence on
				# ntake**(-2/np) is so that we can't possibly get into
				# a situation where a reasonably good fit
				# is too close to some other
				# reasonably good fit.
				# Mind you, there's no reason to ignore them.  We just
				# make a small increment to the counter, so we will pick
				# up other points, too.
				dist = Num.sum((t[1]-shi.resid())**2)
				if dist < closest:
					closest = dist

			if D and closest<dclose:
				 print 'Close: %g/%g=%g' % (closest, dclose, math.sqrt(closest/dclose))
			if closest > 0.03*dclose:
				o.append( (shi.prms()-current.prms(), shi.resid()) )
				self.na_used += 1
				self.description.append( '%s%d:%d%+-.2g' % ('Aa'[closest<dclose],
									i,
									len(self.history)-score1[ordering[i]],
									logp[ordering[i]]-logp[ordering[0]]) )
				nt += min(1.0, math.sqrt(closest/dclose))
			else:
				self.na_unused += 1
			i -= 1
		return (i, nt, o)


	def choose(self):
		if D:
			print "CHOOSE"
			sys.stdout.flush()
		tries = 0
		while tries < 20*self.np:
			i, nt, o = self.choose_guts()
			if nt >= self.ntake:
				print 'DESC:', ' '.join(self.description)
				sys.stdout.flush()
				# Get rid of unnecessary history:
				xtra = i - 5 - len(self.history)//2
				if xtra > 0:
					self.history[:xtra] = []
				return o
			nadd = 1 + int(round(1.2*(self.ntake*1.2 - nt)))
			if D:
				print "CHOOSE needs %d more" % nadd
				sys.stdout.flush()
			while nadd>=0 and len(self.initial)>0:
				nadd -= self.add( self.initial.pop(-1), 0)
				tries += 1
			while nadd >= 0:
				nadd -= self.add( self.get_new(), -1)
				tries += 1
		if D:
			sys.stdout.flush()
			sys.stderr.flush()
		raise RuntimeError, "Can't manage to choose enough points."


	def set_current(self, setting):
		self._last = self._current
		self._current = setting


	def current(self):
		return self._current


	def last(self):
		return self._last


	def go(self):
		while len(self.initial)>0 and self.initial[-1].badspot():
			self.initial.pop(-1)
		if len(self.initial) == 0:
			raise ValueError, "All the starting positions are bad."
		x = self.initial.pop(-1)
		self.add( x )
		self._current = x


	def add_initial(self, x):
		"""Returns 1 once there is enough data. Otherwise returns 0."""
		# Check for exact dups without calculating residual.
		assert isinstance(x, position)
		for t in self.initial:
			if x.prms() == t.prms():
				return 0

		self.initial.append(x)
		enough = 0
		while len(self.initial) > 24*self.np:
			self.initial.pop(0)
			enough = 1
		return enough


	def add(self, x, location=-1):
		"""Add a point to the history list if it is generally good.
		Location tells you whether to add to the beginning (0) or end (-1)
		of the history list.
		If adding on the end,
		if the new point is very close to a previous point on the list,
		delete the previous point.
		If adding to the beginning, only add if there is no close point
		later in the list.
		It returns the net number of points added.
		"""

		if x.badspot():
			return 0

		dclose = self.SMALL_PRE*self.np*(self.SMALL_VOL/self.np)**(2.0/self.np)
		i = 0
		ndel = 0
		while i < len(self.history):
			t = self.history[i]
			# We don't want duplicate (or near-duplicate) points.
			# The dependence on
			# ntake**(-2/np) is so that we can't possibly get into
			# a situation where reasonably good fit is too close to some other
			# reasonably good fit.
			dist = Num.sum((t.resid()-x.resid())**2)
			if dist < 0.01 * dclose:
				if location == 0:
					if D:
						print 'ADD - dropped: tooclose:', dist, dclose
					return 0
				del self.history[i]
				ndel += 1
			else:
				i += 1

		if location == -1:
			self.history.append(x)
		else:
			self.history.insert(0, x)

		if D:
			print 'ADD (deleted %d)' % ndel
		return 1-ndel



	def describe(self):
		o = {}
		o['na_used'] = self.na_used
		o['na_unused'] = self.na_unused
		o['ni_used'] = self.ni_used
		o['nn_used'] = self.nn_used
		o['deriv_pass'] = self.deriv_pass
		o['newscale'] = '%.1e' % self.newscale
		o['choose'] = ', '.join(self.description)
		return avio.concoct(o)


def get_localfit(selectprms):
	print 'GET_LOCALFIT'
	np = selectprms.np
	MAXPASS = 6 + np/2
	selectprms.narrow()
	selectprms.deriv_pass = 0
	while selectprms.deriv_pass < MAXPASS:
		const, coef, more1, more2, not_locally_linear = get_1_localfit(selectprms)
		if more1 or (0.7*more2)>random.random():
			if random.random()<0.70:
				selectprms.widen()
		else:
			break
		selectprms.deriv_pass += 1
	return (const, coef, not_locally_linear)


def _tgf_fn(p, c):
	return p


def test_get_localfit():
	NH = 100
	ND = 4
	c = None
	selectprms = archiver(ND, Num.identity(ND), problem_definition(_tgf_fn, None), timer())
	for i in range(NH):
		p = RandomArray.multivariate_normal(Num.zeros((ND,)), Num.identity(ND))
		selectprms.add( position(p, _tgf_fn))
	const, coef, nll = get_localfit(selectprms)
	print 'const', const
	print 'coef', coef
	const_adjust = const - Num.matrixmultiply(selectprms.current().prms(), coef)
	print 'const_adj', const_adjust
	assert Num.sum(Num.absolute(const_adjust)) < 1e-6



def sigma(x):
	xr = Num.ravel(x)
	avg = Num.sum(xr)/xr.shape[0]
	return math.sqrt( Num.sum((xr-avg)**2)/(xr.shape[0]-1) )


def get_1_localfit(selectprms):
	SVLIM = 1e-10
	SVLOGLIM = 6
	TINY = 1e-20
	x = selectprms.choose()
	np = selectprms.np
	vbf = g_localfit.err_before_fit(x)
	coef, const, errs, sv, rank = g_localfit.localfit(x, SVLIM)
	print "np=", np, 'rank=', rank
	print 'err_before_fit=', Num.sum(vbf), 'err_after=', Num.sum(errs)
	if Num.sum(vbf)/vbf.shape[0] > 1000.0:
		print '#WARN: VarianceBeforeFit=', vbf
	if Num.sum(errs)/errs.shape[0] > 1000.0:
		print '#WARN: Errs=', errs

	vr = (errs+TINY)/(vbf+TINY)
	print 'maxr=', max(vr), 'minr=', min(vr), 'medr=', gpkmisc.N_median(vr), 'gt0.5=', Num.sum(vr>0.5), 'n=', vr.shape[0]
	nll = (max(vr)>0.9) + (gpkmisc.N_median(vr)>0.5) + (Num.sum(vr)/vr.shape[0])
	nll += (max(vr)>0.7) + (gpkmisc.N_median(vr)>0.3) + (Num.sum(vr>0.5)>math.sqrt(vr.shape[0]))
	nll += (max(vr)>0.5) + (gpkmisc.N_median(vr)>0.2)
	if nll > 1.0:
		die.note('Maximum localfit residual', max(vr))
		die.note('Median localfit residual', gpkmisc.N_median(vr))
		die.note('Num localfit residual>0.5', '%d/%d' % (Num.sum(vr>0.5), vr.shape[0]))
		die.warn("Residuals don't seem to be locally linear.")
	assert np+1 >= rank
	assert len(sv) <= np+1
	assert coef.shape[1] == np
	more1 = np+1 > rank  or  np >= len(x)
	sigsv = sigma(Num.log(Num.array(sv)+TINY))
	if D:
		print "np=", np, 'rank=', rank, 'len(x)=', len(x)
		print 'sigsv=', sigsv, 'err_before_fit=', Num.sum(vbf), 'err_after=', Num.sum(errs)
		print 'get_1_localfit.sv=', sv
	more2 = sigsv > (SVLOGLIM*float(len(x))/float(np)) or 1.2*(np+1)>=len(x)
	if D:	print 'MORE:', more1, more2
	return (const, coef, more1, more2, nll)



def test_llsl():
	test_llsl_1()
	test_llsl_1o()
	test_llsl_2u()
	test_llsl_2()

def test():
	test_llsl()
	test_get_localfit()
	test_stepper()




def diag_variance(start):
	return gpkmisc.make_diag(gpkmisc.vec_variance(start))






def go(argv):
	"""Run an optimization from command line flags."""
	import load_mod
	global MINIMIZE

	if len(argv) <= 1:
		print __doc__
		die.exit(0)
	python = None
	out = None
	NI = None
	arglist = argv[1:]
	while len(arglist) > 0  and arglist[0][0] == '-':
		arg = arglist.pop(0)
		if arg == '-o':
			out = arglist.pop(0)
		elif arg == '-py':	# path/module
			python = arglist.pop(0)
		elif arg == '-NI':
			NI = int(arglist.pop(0))
		elif arg == '-m':
			MINIMIZE = float(arglist.pop(0))
		elif arg == '--':
			break
		else:
			die.die("Unrecognized flag: %s" % arg)
	
	assert python is not None, "Need to use the -py flag."

	mod = load_mod.load_named_module(python)
	print "# mod=", mod

	if out:
		logfd = open(out, "w")
	else:
		logfd = None


	if not hasattr(mod, "start"):
		start = _read(sys.stdin)
	else:
		start = Num.asarray(mod.start(arglist), Num.Float)
		if len(start.shape) == 1:
			start = [start]

	if NI is None:
		NI = mod.NI
	print "# NI=", NI

	if hasattr(mod, "V"):
		V = Num.asarray(mod.V(start), Num.Float)
	elif _start_is_list_a(start) and len(start)>1:
		V = diag_variance(start)
	else:
		V = Num.identity(start[0].shape[0], Num.Float)

	if hasattr(mod, "init"):
		logptr = mod.init(V.shape, NI, mod.c, arglist)
	else:
		logptr = def_logger(V.shape, NI, mod.c, arglist)

	showvec = getattr(mod, 'showvec', 1)

	fixer = getattr(mod, 'fixer', None)

	sys.stdout.flush()
	x = SQstepper(mod.resid, len(start[0]), V, mod.c, locations=start,
			positions=getattr(mod, "positions", []),
			minimize=getattr(mod, "minimize", MINIMIZE)
			)

	sys.stdout.writelines('[P]\n')
	for i in range(NI):
		x.step(showvec=showvec)
		p = x.prms()
		sys.stdout.flush()
		if logfd is not None:
			logfd.writelines('# ' + x.status() + '\n')
			_print(logfd, '%d'%i , p)
			logfd.flush()
		if logptr is not None:
			logptr.add(p, i)
	if logptr is not None:
		logptr.finish(sys.stdout)



if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	try:
		go(sys.argv)
	except:
		die.catch('Unexpected exception')
		raise


