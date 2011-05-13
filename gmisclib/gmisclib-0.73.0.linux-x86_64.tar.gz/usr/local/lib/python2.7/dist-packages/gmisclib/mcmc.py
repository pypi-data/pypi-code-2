"""Adaptive Markov-Chain Monte-Carlo algorithm.
This can be used to generate samples from a probability distribution,
or also as a simulated annealing algorithm for maximization.
This can be imported and its functions and classes can be used.

The central interfaces are the L{mcmc.BootStepper} class, and within
it, the C{step()} method is used iteratively to take a Markov step.

The algorithm is described in Kochanski and Rosner 2010,
and earlier versions have been used in ZZZ.
It evolved originally from amoeba_anneal (in Numerical Recipes, Press et al.).
The essential feature is that it keeps a large archive of previous positions
(possibly many times more than C{N} of them). It samples two positions
from the archive and subtracts them to generate candidate steps.
This has the nice property that when sampling from a multivariate
Gaussian distribution, the candidate steps match the distribution nicely.

It can be operated in two modes (or set to automatically switch).
One is optimization mode where it heads for the maximum of the probability
distribution.   The other mode is sampling mode, where it
asymptotically follows a Markov sampling procedure and has the
proper statistical properties.
"""
from __future__ import with_statement

import math
import types
import random
import bisect
import threading

import numpy

import die
import gpkmisc
import g_implements
import multivariate_normal as MVN

Debug = 0
MEMORYS_WORTH_OF_PARAMETERS = 1e8



class problem_definition(object):
	"""This class implements the problem to be solved.
	It's overall function in life is to compute the probability that a given
	parameter vector is acceptable.    Mcmc.py then uses that to run a
	Markov-Chain Monte-Carlo sampling.
	You may want to derive a class from this and override all the functions defined here,
	or implement your own class with the same functions.
	(Of course, in that case, it can contain extra functions also.)
	
	For instance, it can be a good idea to define a function
	"model" that computes the model that you are fitting to data
	(if that is your plan).   Then logp() can be something
	like -numpy.sum((self.model()-self.data)**2).
	Also, it can be good to define a "guess" function that computes
	a reasonable initial guess to the parameters, somehow.
	"""

	@g_implements.make_optional
	@g_implements.make_varargs
	def __init__(self):
		pass

	def logp(self, x):
		"""Compute the log of the probability density at C{x}.
		@param x:a parameter vector
		@type x: numpy.ndarray
		@return: The log of the probability that the model assigns to parameters x.
		@rtype: float
		@raise NotGoodPosition: This exception is used to indicate that the position
			x is not valid.   This is equivalent to returning an extremely negative
			logp.
		"""
		raise RuntimeError, "Virtual method"
	
	def fixer(self, x):
		"""This is called on each candidate position
		vector.    Generally, it is used to restrict the possible
		solution space by folding position vectors that escape outside the solution space back into
		the solution space.    It can also allow for symmetries in equations.

		Formally, it defines a convex region.   All vectors outside the region are mapped
		into the region, but the mapping must be continuous at the boundary.
		(More precisely, logp(fixer(x)) must be continuous everywhere that logp(x) is continuous,
		including the boundary.)   For instance, mapping x[0] into abs(x[0]) defines a convex region
		(the positive half-space), and the mapping is continuous near x[0]=0.

		Additionally, it may re-normalize parameters at will subject to the restriction
		that logp(fixer(x))==logp(x).
		For instance, it can implement a constraint that sum(x)==0 by mapping
		x into x-average(x), so long as the value of logp() is unaffected by that
		substitution.
		other folds can sometimes lead to problems.

		@param x:a parameter vector
		@type x: numpy.ndarray
		@return: a (possibly modified) parameter vector.
		@rtype: numpy.ndarray
		@attention: Within a convex region (presumably one that contains the optimal x),
			fixer must *not* change the value of logp(): logp(fixer(x)) == logp(x).

		@raise NotGoodPosition: This exception is used to indicate that the position
			x is not valid.   Fixer has the option of either
			mapping invalid parameter vectors into valid ones
			or raising this exception.
		"""
		raise RuntimeError, "Virtual method"

	@g_implements.make_optional
	def log(self, p, i):
		"""Some code calls this function every iteration
		to log the current state of the MCMC process.
		@param p: the current parameter vector, and
		@param i: an integer iteration counter.
		@return: nothing.
		"""
		raise RuntimeError, "Virtual method"

	# @g_implements.make_optional
	# def guess(self):
		# """Some code calls this function at the beginning
		# of the MCMC process to seed the iteration.
		# @return: a list of guess vectors; each guess vector is
		# 	suitable for passing to self.fixer() or self.logp() as x.
		# """
		# raise RuntimeError, "Virtual method"


class problem_definition_F(problem_definition):
	@g_implements.make_optional
	@g_implements.make_varargs
	def __init__(self, logp_fcn, c, fixer=None):
		problem_definition.__init__(self)
		self.c = c
		self._fixer = fixer
		# assert logp_fcn is None or callable(logp_fcn)
		assert callable(logp_fcn)
		self.lpf = logp_fcn

	def logp(self, x):
		return (self.lpf)(x, self.c)

	logp.__doc__ = problem_definition.logp.__doc__

	
	def fixer(self, x):
		if self._fixer is not None:
			return (self._fixer)(x, self.c)
		return x

	fixer.__doc__ = problem_definition.fixer.__doc__





_Ntype = type(numpy.zeros((1,), numpy.float))



class position_base(object):
	"""This class is used internally in the MCMC sampling process to
	represent a position.   It stores a parameter vector, a reference to
	the problem definition, and (optionally) caches computed values
	of log(P).
	"""
	@g_implements.make_optional
	def __init__(self, x, problem_def):
		"""You need this function and
		this signature if you are going to pass
		it to make_list_of_positions(), but not necessarily
		otherwise.
		"""
		g_implements.check(problem_def, problem_definition)
		self.pd = problem_def
		# print "position:x=", x
		tmp = numpy.array(x, numpy.float, copy=True)
		tmp = self.pd.fixer(tmp)
		assert isinstance(tmp, _Ntype), "Output of fixer() is not numpy array."
		assert tmp.shape == x.shape, "Fixer output[%s] must match shape of input[%s]." % (str(tmp.shape),  str(x.shape))
		# self.x = numpy.array(tmp, copy=True)
		self.x = tmp
		self._uid = hash(self.vec().tostring())


	# def __deepcopy__(self, memo):
		# """Don't copy andy deeper than this."""
		# return position_base(self.x, self.pd)


	def logp(self):
		"""Compute the log of the probability for the position.
		"""
		raise RuntimeError, "Virtual Function"


	def logp_nocompute(self):
		"""Shows a recent logp value.  It does not compute
		a value unless none has ever been computed.
		"""
		raise RuntimeError, "Virtual Function"


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount.
		@param shift: How much of a move to make to the new position.
		@type shift: numpy.ndarray
		@param logp: (optional)  If this is supplied, is is used to set the
			log(P) value for the newly created position structure.
		@type logp: float or None
		@return: a new position
		@rtype: L{position_base} or a subclass
		"""
		raise RuntimeError, "Virtual Function"


	def prms(self):
		"""The result of this function is to be handed to problem_definition.logp().
		This result must contain all the information specifying the position.
		Normally, this is a vector of floats, but concievably, you could include other information.
		"""
		return self.x


	def vec(self):
		"""Returns a numpy vector, for mathematical purposes.
		The result should contain all the information specifying the position;
		if not all, it should at least contain all the information that can be
		usefully expressed as a vector of floating point numbers.

		Normally, self.vec() and self.prms() are identical.
		"""
		return self.x


	@g_implements.make_optional
	def __repr__(self):
		return '<POSbase %s>' % str(self.x)


	def __cmp__(self, other):
		"""This is used when the archive is sorted."""
		dd = 0
		try:
			a = self.logp_nocompute()
		except NotGoodPosition:
			dd -= 2
			a = 0.0		# only relevant when both are uncomputable.
		try:
			b = other.logp_nocompute()
		except NotGoodPosition:
			dd += 2
			b = 0.0		# only relevant when both are uncomputable.
		return dd or cmp(a, b)


	def uid(self):
		return self._uid


class position_repeatable(position_base):
	"""This is for the common case where logp is a well-behaved
	function of its arguments.   It caches positions and their corresponding
	values of log(P).
	"""
	EPS = 1e-7
	HUGE = 1e38
	CACHE_LIFE = 50
	FIXER_CHECK = 100
	"""How often should we recompute cached values to make sure that the
	same parameters always lead to the same results?"""
	# CACHE_LIFE = 1	# For debugging only.

	@g_implements.make_optional
	def __init__(self, x, problem_def, logp=None):
		"""
		@param x: 
		@type x: numpy.ndarray
		@type problem_def: L{problem_definition} or a subclass thereof.
		@type logp: float or None
		@param logp: the value of C{log(P)} at C{x}, or None to indicate that it
			hasn't been computed yet.
		@except ValueError: if sanity check is failed.
		@except NotGoodPosition: from inside L{problem_definition.logp}.
		"""
		position_base.__init__(self, x, problem_def)
		if logp is not None and not (logp < self.HUGE):
			raise ValueError("Absurdly large value of logP", logp, self.x)
		self.cache = logp
		if logp is None:
			self.cache_valid = -1
		else:
			self.cache_valid = self.CACHE_LIFE
		if random.random()*self.FIXER_CHECK < 1.0:
			# This is a sanity check: 1% of the time we make sure that
			# the supplied value of log(P) is consistent with what is yielded by C{problem_def}.
			# Note that self.pd.fixer() gets called inside position_base inside
			# position_repeatable.
			tmp = position_repeatable(self.x, problem_def)
			tlp = tmp.logp()
			slp = self.logp()
			if abs(tlp - slp) > 0.1 + self.EPS*abs(tlp+slp):
				# Ideally, EPS will be zero. But, you sometimes get roundoff
				# errors in the fixer early on in an optimization when the fit
				# is still awful.  So, it might allow past some non-idempotent functions,
				# but only for a set of parameters that are so wild and awful
				# that no one should really cares.   This is a bit of a kluge, but not a bad one.
				raise ValueError, "Fixer is not idempotent.  Logp changes from %s to %s." % (self.logp(), tmp.logp())



	def invalidate_cache(self):
		"""This can be called when the mapping between parameters (x)
		and value changes.   You might use it if you wanted to
		change the probability distribution (i.e. C{log(P)}).
		"""
		self.cache_valid = -1


	def logp(self):
		if self.cache_valid <= 0:
			try:
				logp = self.pd.logp(self.prms())
			except NotGoodPosition:
				logp = None

			if logp is not None and not (logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			if(self.cache_valid==0 and
				((self.cache is None)!=(logp is None)
				or
				abs(logp - self.cache) > 0.1 + 1e-8*(abs(logp)+abs(self.cache))
				)):
				raise ValueError, 'Recomputing position cache; found mismatch %s to %s' % (self.cache, logp)
			self.cache = logp
			self.cache_valid = self.CACHE_LIFE
		self.cache_valid -= 1
		if self.cache is None:
			raise NotGoodPosition
		return self.cache


	def logp_nocompute(self):
		if self.cache_valid < 0:
			return self.logp()
		if self.cache is None:
			raise NotGoodPosition
		return self.cache


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount."""
		return position_repeatable(self.vec() + shift, self.pd, logp=logp)


	def __repr__(self):
		if self.cache_valid > 0:
			s = str(self.cache)
		elif self.cache_valid == 0:
			s = "<cache expired>"
		else:
			s = "<uncomputed>"
		return '<POSr %s -> %s>' % (str(self.prms()), s)



class position_nonrepeatable(position_base):
	"""This is for the (unfortunately common) case where logp
	is an indpendent random function of its arguments.  It does
	not cache as much as L{position_repeatable}.
	Arguments are analogous to L{position_repeatable}.
	"""
	HUGE = 1e38

	@g_implements.make_optional
	def __init__(self, x, problem_def, logp=None):
		position_base.__init__(self, x, problem_def)
		if logp is None:
			self.cache = []
		else:
			if not (logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			self.cache = [ logp ]
		self.CSIZE = 5



	def logp(self):
		if random.random() > self.CSIZE / float(self.CSIZE + len(self.cache)): 
			logp = random.choice(self.cache)
		else:
			try:
				logp = self.pd.logp(self.prms())
			except NotGoodPosition:
				logp = None

			if not (logp is None or logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			self.cache.append(logp)
		if logp is None:
			raise NotGoodPosition
		return logp


	def logp_nocompute(self):
		if self.cache:
			tmp = random.choice(self.cache)
			if tmp is None:
				raise NotGoodPosition
		else:
			tmp = self.logp()
		return tmp


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount."""
		return position_nonrepeatable(self.vec() + shift, self.pd, logp=logp)


	def __repr__(self):
		if len(self.cache):
			s1 = ""
			mn = None
			mx = None
			for q in self.cache:
				if q is None:
					s1 = "BAD or"
				else:
					if mx is None or q>mx:
						mx = q
					if mn is None or q<mx:
						mn = q
			s = "%s%g to %g" % (s1, mn, mx)
		else:
			s = "<uncomputed>"
		return '<POSnr %s -> %s>' % (str(self.prms()), s)


class _empty(object):
	"""Just a singleton marker."""
	pass


class position_history_dependent(position_base):
	"""This is for the case where logp is a history-dependent
	function of its arguments.   This is the most general, most
	expensive case.
	"""
	EMPTY = _empty
	HUGE = 1e38

	@g_implements.make_optional
	def __init__(self, x, problem_def, logp=None):
		position_base.__init__(self, x, problem_def)
		if logp is None:
			self.cache = self.EMPTY
		else:
			if not (logp < self.HUGE):
				raise ValueError("Absurdly large value of logP", logp, self.x)
			self.cache = logp



	def logp(self):
		logp = self.pd.logp(self.prms())
		if not (logp is None or logp < self.HUGE):
			raise ValueError("Absurdly large value of logP", logp, self.x)
		self.cache = logp
		if logp is None:
			return NotGoodPosition
		return logp


	def logp_nocompute(self):
		if self.cache is self.EMPTY:
			return self.logp()
		if self.cache is None:
			return NotGoodPosition
		return self.cache


	def new(self, shift, logp=None):
		"""Returns a new position, shifted by the specified amount."""
		return position_history_dependent(self.vec() + shift, self.pd, logp=logp)


	def __repr__(self):
		if self.cache is self.EMPTY:
			s = "<uncomputed>"
		else:
			s = str(self.cache)
		return '<POSr %s -> %s>' % (str(self.prms()), s)


class T_acceptor(object):
	"""This class implements a normal Metropolis-Hastings
	acceptance of steps.
	"""
	def __init__(self, T=1.0):
		"""You can change the temperature to do simulated annealing.
		@param T: temperature
		@type T: float
		"""
		assert T >= 0.0
		self._T = T

	def T(self):
		"""@return: the system temperature.
		@rtype: L{float}
		"""
		return self._T

	def __call__(self, delta):
		"""Accept a step or not?
		@param delta: The proposed step gives C{delta} as the change in
			C{log(probability)}.
		@type delta: float
		@return: should it be accepted or not?
		@rtype: C{bool}
		"""
		return delta > -self._T*random.expovariate(1.0)


class stepper(object):
	"""This is your basic stepper class that incrementally will
	give you a Markov-Chain Monte-Carlo series of samples from
	a probability distribution.
	"""

	@g_implements.make_varargs
	def __init__(self):
		self.since_last_rst = 0
		self.resetid = 0
		self.last_reset = None
		# self.last_failed should reflect the success or failure of the most recently
		# completed step.   It is None if the last step succeeded; it is the
		# most recently rejected position object if the last step failed.
		self.last_failed = None
		self.lock = threading.RLock()
		self.acceptable = T_acceptor(1.0)
		"""Acceptable is a function that decides whether or not a step is OK.
		You can replace it if you want, but the class should be equivalent
		to L{T_acceptor}."""


	def step(self):
		"""In subclasses, this takes a step and returns 0 or 1,
		depending on whether the step was accepted or not."""
		self.since_last_rst += 1
		return None


	def prms(self):
		"""@return: The current parameters
		@rtype: C{numpy.ndarray}
		"""
		return self.current().prms()


	# def prmlist(self):
		# """Returns all stored positions."""
		# raise RuntimeError, "Virtual Function"
	
	def status(self):
		"""Provides some printable status information in a=v; format."""
		raise RuntimeError, "Virtual Function"

	
	def reset(self):
		"""Called internally to mark when the optimization
		has found a new minimum.   [NOTE: You might also call it
		if the function you are minimizing changes.]
		"""
		# print 'stepper.reset', threading.currentThread().getName()
		with self.lock:
			self.since_last_rst = 0
			self.resetid += 1

	def reset_id(self):
		"""Use this to tell if the stepper has been reset since you last
		looked at it.
		"""
		return self.resetid

	def needs_a_reset(self):
		"""Decides if we we need a reset.    This checks
		to see if we have a new record logP that exceeds
		the old record.   It keeps track of the necessary
		paperwork.
		"""
		current = self.current()
		# print 'stepper.needs_a_reset', threading.currentThread().getName()
		with self.lock:
			if self.last_reset is None:
				self.last_reset = current
				rst = False
			else:
				rst = current.logp_nocompute() > self.last_reset.logp_nocompute() + self.acceptable.T()*0.5
				# rst = current.logp_nocompute() > self.last_reset.logp_nocompute()
				if rst:
					self.last_reset = current
		if rst and Debug>1:
			print '# RESET: logp=', current.logp_nocompute()
		return rst


	def _set_failed(self, f):
		with self.lock:
			self.last_failed = f

	def current(self):
		"""@return: the current position.
		@rtype: L{position_base}
		"""
		with self.lock:
			return self._current

	
	def _set_current(self, newcurrent):
		"""@raise NotGoodPosition: if newcurrent doesn't have a finite logp() value.
		"""
		with self.lock:
			# logp_nocompute() will raise a NotGoodPosition exception
			# so this essentially asserts that the current position is good.
			newcurrent.logp_nocompute()
			self._current = newcurrent



class adjuster(object):
	Z0 = 1.5
	DZ = 0.3
	TOL = 0.2
	STABEXP = 1.0

	def __init__(self, F, vscale, vse=0.0, vsmax=1e30):
		assert 0.0 < F < 1.0
		self.lock = threading.Lock()
		self.vscale = vscale
		self.F = F
		# self.np = np
		self.state = 0
		self.vse = vse
		self.reset()

		self.vsmax = vsmax
		"""Used when the acceptance probability is larger than 25%.
		Large acceptance probabilities
		can happen if the probability is everywhere about
		equal.   (E.g. a data fitting problem with almost
		no data)"""

	def reset(self):
		# print 'adjuster.reset', threading.currentThread().getName()
		with self.lock:
			self.z = self.Z0
			self.since_reset = 0
			self.ncheck = self._calc_ncheck()
			self.blocknacc = 0
			self.blockntry = 0
		# print "#ADJUSTER RESET"

	def _calc_ncheck(self):
		"""This estimates when to make the next check for statistically significant
		deviations from the correct step acceptance rate.
		"""
		assert self.z >= self.Z0
		ss =  max( -self.z/math.log(1-self.f()), -self.z/math.log(self.f()) )
		"""Ss is the fewest samples where you could possibly
		detect statistically significant deviations
		from getting a fraction self.F of steps accepted."""
		assert ss > 3.0
		# The "100" is just there because checking the step acceptance rate isn't very expensive,
		# so we might as well guard against absurdly long check intervals.
		return min(100, int(math.ceil(ss)))
	
	def f(self):
		"""This allows the desired fraction of accepted steps to
		depend on self.vscale.
		@note: This method should only be called with C{self.vse != 0}
			where self.vscale can normally be expected to be fairly close to unity,
			and where small values of C{self.vse} indicate trouble.
			In the L{mcmc.Bootstepper.step_boot} case this is true.
		"""
		# Ideally, we'd like self.f()==self.F for
		# greatest efficiency, but that can fail badly if the acceptance
		# probability is always smaller than self.F.   One example is
		# where this happens is if the maximum is at a corner of an
		# allowable region, such as:
		# log(P) = { w<0 or x<0 or y<0 or z<0 : -infinity,
			 	# else: -(x+y+z+w)
			# }.
		# In such a case, trying to maintain the optimal step acceptance
		# can drive vscale to zero, which is not good for the convergence
		# rate.   The function chosen here gives up some efficiency
		# to avoid such a disaster.  
		return self.F * min(1.0, self.vscale**self.vse)


	def inctry(self, accepted):
		# print 'adjuster.inctry', threading.currentThread().getName()
		with self.lock:
			self.since_reset += 1
			self.blockntry += 1
			self.blocknacc += accepted
	
			# Only check occasionally.
			if self.blockntry > self.ncheck:
				self._inctry_guts()


	def _inctry_guts(self):
		"""Called under lock!
		We check that the observed fraction of accepted
		steps is consistent with a Binomial distribution.
		If not, we try updating self.vscale.
		"""
		EPS = 1e-6
		Flow = self.f() * (1.0 - self.TOL)
		Fhi = self.f() * (1.0 + self.TOL)
		lPH0low = self.blocknacc*math.log(Flow) + (self.blockntry-self.blocknacc)*math.log(1-Flow)
		lPH0hi = self.blocknacc*math.log(Fhi) + (self.blockntry-self.blocknacc)*math.log(1-Fhi)
		Phat = (self.blocknacc + EPS)/(self.blockntry + 2*EPS)
		sigmaP = math.sqrt(self.f() * (1-self.f()) / self.blockntry)
		lPH1 = self.blocknacc*math.log(Phat) + (self.blockntry-self.blocknacc)*math.log(1-Phat)
		# print '#NCHECK bnacc=', self.blocknacc, self.blockntry, lPH0low, lPH0hi, lPH1, self.z

		if (Phat>Fhi and lPH1-lPH0hi > self.z) or (Phat<Flow and lPH1-lPH0low > self.z):
			# The fraction of accepted steps is inconsistent with the range
			# from Flow to Fhi -- in other words, we're reasonably sure the acceptance
			# rate is substantially wrong.

			delta = math.log(Phat/self.f())
			delta = min(max(delta, -self.TOL), self.TOL)
			self.vscale *= math.exp(delta*self.STABEXP)
			if self.vscale > self.vsmax:
				self.vscale = self.vsmax
			if Debug>2:
				print '#NCHECK step acceptance rate is %.2f vs. %.2f:' % (Phat, self.f()), 'changing vscale to', self.vscale
				print '#NCHECK ADJ vscale=', self.vscale, self.z, self.blocknacc, self.blockntry, delta
			self.blockntry = 0
			self.blocknacc = 0
			self.state = -1
			self.ncheck = self._calc_ncheck()
		elif Phat>Flow and Phat<Fhi and 2.0*sigmaP/self.f() < self.TOL:
			# We're as accurate as we need to be.
			# Therefore, we might as well restart the counters
			# in case the process is non-stationary.
			self.blockntry = 0
			self.blocknacc = 0
			self.state = 1
			self.ncheck = self._calc_ncheck()
			# print '#NCHECK close enough', 'phat=', Phat, 'sigmaP=', sigmaP
		else:
			# Doing OK.  The step acceptance rate is not
			# known to be incorrect.
			self.z += self.DZ
			self.state = 0
			self.ncheck = self.blockntry + self._calc_ncheck()
			# print "#NCHECK OK", self.ncheck, 'z=', self.z


	def vs(self):
		"""We stick in the factor of random.lognormvariate()
		so that all sizes of move are possible and thus we
		can prove that we can random-walk to any point in
		a connected region.   This makes the proof of
		ergodicity simpler.
		"""
		assert type(self.vscale)==types.FloatType
		return random.lognormvariate(0.0, self.TOL/2.0)*self.vscale


	def status(self):
		with self.lock:
			tmp = (self.blocknacc, self.blockntry, self.state)
		return tmp






def start_is_list_a(start):
	"""Is the argument a sequence of numpy arrays?
	"""

	for (i, tmp) in enumerate(start):
		if not isinstance(tmp, _Ntype):
			if i > 0:
				raise TypeError, "Sequence is not all the same type"
			return False
	return len(start) > 0


def start_is_list_p(start):
	"""Is the argument a sequence of position_base objects?
	"""

	for (i, tmp) in enumerate(start):
		if not g_implements.impl(tmp, position_base):
			if i > 0:
				raise TypeError, "Sequence is not all the same type"
			return False
	return len(start) > 0



class NoBoot(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)

class NotGoodPosition(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)



def make_list_of_positions(x, PositionClass, problem_def):
	"""Turn almost anything into a list of position_base objects.
	You can hand it a sequence of numpy vectors
	or a single 1-dimensional numpy vector;
	a sequence of position_base objects
	or a single 1-dimensional position_base object.

	@precondition: This depends on PositionClass being callable as
		PositionClass(vector_of_doubles, problem_definition).
	"""
	o = []
	if start_is_list_a(x):
		assert len(x) > 0, "Zero length list of arrays."
		for t in x:
			if len(o) > 0:
				assert t.shape == (o[0].vec().shape[0],)
			# If the parameters are identical,
			# we can share position structures,
			# and reduce the number of times we need
			# to evaluate logp(x, c).
			if len(o)>0 and numpy.alltrue(numpy.equal(o[-1].vec(), t)):
				# print 'SAME:', t, self.current()
				o.append( o[-1] )
			else:
				# print 'DIFF:', t
				o.append( PositionClass(t, problem_def) )
	elif start_is_list_p(x):
		assert len(x) > 0, "Zero length list of positions."
		o = []
		for t in x:
			g_implements.check(t, PositionClass)
			if len(o) > 0:
				assert t.vec().shape[0] == (o[0].vec().shape[0],)
			if len(o)>0 and numpy.alltrue(numpy.equal(t.vec(), o[-1].vec())):
				o.append( o[-1] )
			else:
				# print 'DIFF:', t
				o.append( t )
	elif g_implements.impl(x, PositionClass):
		o = [x]
	elif isinstance(x, _Ntype) and len(x.shape)==1:
		o = [ PositionClass(x, problem_def) ]
	else:
		raise TypeError, "Cannot handle type=%s for x.  Must implement %s or be a 1-dimensional numpy array." % (type(x), repr(PositionClass))
	return o



def _check_list_of_positions(x):
	if not isinstance(x, list):
		raise TypeError, "Not a List (should be a list of positions)"
	for (i, t) in enumerate(x):
		failure = g_implements.why(t, position_base)
		if failure is not None:
			raise TypeError, "x[%d] does not implement position_base: %s" % (i, failure)


class hashcounter_c(dict):
	def incr(self, x):
		try:
			self[x] += 1
		except KeyError:
			self[x] = 1

	def decr(self, x):
		tmp = self[x]
		if tmp == 1:
			del self[x]
		elif tmp < 1:
			raise ValueError("More decrements than increments", x)
		else:
			self[x] = tmp-1





class Archive(object):
	"""This maintains a list of all the recent accepted positions."""
	#: Always keep the list of positions sorted.
	#: This improves mimimization performance at the cost of a distorted probability distribution.
	SUPHILL = 'hillclimb'
	#: Never sort the list.    Best if you really want an exact Monte Carlo distribution.
	SSAMPLE = 'sample'
	#: Sort the list only when logp() is making substantial improvements.
	SANNEAL = 'intermediate'


	def __init__(self, lop, np_eff, strategy=SANNEAL, maxArchSize=None, alpha=None):
		assert strategy in (self.SSAMPLE, self.SANNEAL, self.SUPHILL)
		assert len(lop) > 0
		self.xlop = []
		self.lop = lop
		self.strategy = strategy
		self.sorted = False
		if self.strategy == self.SANNEAL:
			self.sort()
			self.sorted = True
		self.np_eff = np_eff
		self.since_last_rst = 0
		self.lock = threading.Lock()
		self._hashes = hashcounter_c()
		for p in self.lop:
			self._hashes.incr(p.uid())

		if maxArchSize is None:
			maxArchSize = MEMORYS_WORTH_OF_PARAMETERS // self.np_eff
		#: The minimum length for the archive.  This is chosen to be big enough so that
		#: all the parallel copies probably span the full parameter space.
		self.min_l = self.np_eff + int(round(2*math.sqrt(self.np_eff))) + 3
		if maxArchSize < self.min_l:
			raise ValueError, "maxArchSize is too small for trustworthy operation: %d < min_l=%d (npeff=%d)" % (maxArchSize, self.min_l, self.np_eff)
		self.max_l = maxArchSize
		self.alpha = alpha
		self.n_prmlist = self.min_l


	def distinct_count(self):
		"""How many distinct values of the parameters are there in the archive?"""
		with self.lock:
			return len(self._hashes)
	

	def prmlist(self, n):
		assert n > 0
		with self.lock:
			# print 'prmlist.n=', n, len(self.lop), len(self.xlop)
			self.n_prmlist = n
			# return list(self.xlop + self.lop)
			rv = self.xlop + self.lop
			return rv[max(0,len(rv)-n):]


	def sort(self):
		"""Called under lock. Sort the archive into order of C{logp}."""
		if self.sorted or self.strategy==self.SSAMPLE:
			return
		if Debug:
			die.info( '# Sorting archive' )
		# This uses position.__cmp__():
		self.lop.sort()
		self.sorted = True


	def reset(self):
		"""We sort the archive to speed the convergence to
		the best solution.   After all, if you've just
		gotten a reset, it is likely that you're not at the
		bottom yet, so statistical properties of the distribution
		are likely to be irrelevant.
		"""
		# print 'Archive.reset', threading.currentThread().getName()
		with self.lock:
			self.sort()
			self.truncate(self.min_l)
			self.since_last_rst = 0
	

	def __len__(self):
		with self.lock:
			return len(self.lop)


	def choose(self):
		# print 'Archive.lock', threading.currentThread().getName()
		with self.lock:
			return random.choice( self.lop )


	def truncate(self, desired_length):
		"""Shortens the archive and updates the various counters and statistics.
		@param desired_length: Measured in terms of the number of distinct positions.
		@note: Must be called under lock.
		"""
		assert len(self.lop) > 0
		assert len(self._hashes) <= len(self.lop)
		assert (len(self._hashes)>0) == (len(self.lop)>0)

		j = 0
		while len(self._hashes) > desired_length:
			self._hashes.decr(self.lop[j].uid())
			j += 1
		assert j <= len(self.lop)
		if j > 0:
			self.truncate_hook(self.lop[:j])
			self.xlop.extend(self.lop[:j])
			if len(self.xlop) > self.n_prmlist:
				self.xlop = self.xlop[len(self.xlop)-self.n_prmlist:]
			self.lop = self.lop[j:]
			if Debug > 1:
				die.info('Truncating archive from %d by %d' % (len(self.lop), j))
		elif Debug > 1:
			die.info('Truncate: max=%d, len=%d, nothing done' % (desired_length, len(self.lop)))
		assert len(self._hashes) <= len(self.lop)
		# There is a possibility that we have truncated the current position.
		# This can happen when the archive is sorted, and we have just accepted a step that
		# has worsened log(P).  I wonder if that's a problem?


	Sfac = {SUPHILL: 100, SANNEAL: 5, SSAMPLE: 2}

	def append(self, x, maxdups):
		"""Adds stuff to the archive, possibly sorting the
		new information into place.   It updates all kinds of
		counters and summary statistics.

		@param x: A position to (possibly) add to the archive.
		@type x: L{position_base}
		@return: A one-letter code indicating what happened.  'f' if x
			is a duplicate and duplicates are forbidden.
			'd' if it is a duplicate and there have been
			too many duplicates lately.
			'a' otherwise -- x has been added to the archive.
		@rtype: str
		"""
		# print 'Archive.append', threading.currentThread().getName()
		F = 0.25	# Ideally, this would be BootStepper.F or even the result of adjuster.f().
		with self.lock:
			self.since_last_rst += 1

			assert len(self._hashes) <= len(self.lop)
			uid = x.uid()
			if self.strategy!=self.SSAMPLE and maxdups>0 and self._hashes.get(uid, 0) > maxdups:
				# We don't want the clutter up the archive with lots of duplicates if we're not
				# in sampling mode.
				return 'f'
			self._hashes.incr(uid)

			if not self.sorted or self.strategy==self.SSAMPLE:
				self.lop.append(x)
				self.sorted = False
			else:
				# This uses position.__cmp__():
				bisect.insort_right(self.lop, x)
				# We can't do the following check because (a) it can
				# fail for position_nonrepeatable, and (b) it triggers
				# extra evaluations of logp(), which can be expensive:
				# assert self.lop[-1].logp() >= self.lop[0].logp().
				#
				# Check that we've had enough steps to have had a reasonable chance
				# to have detected a new maximum.
				if self.since_last_rst > self.Sfac[self.strategy]*self.np_eff/F:
					self.sorted = False
					if Debug:
						die.info( '# Archive sorting is now off' )
			self.append_hook(x)
			if Debug > 1:
				die.info('Archive length=%d' % len(self.lop))
			# print "self.lop=", self.lop
			assert len(self._hashes) <= len(self.lop)
			self.truncate( min(int( self.min_l + self.alpha*self.since_last_rst ), self.max_l))
		return 'a'


	def append_hook(self, x):
		pass

	def truncate_hook(self, to_be_dropped):
		pass


class ContPrmArchive(Archive):
	def __init__(self, lop, np_eff, strategy=Archive.SANNEAL, maxArchSize=None, alpha=None):
		"""Append_hook() is called for every element of the archive.
		That function can be replaced in a sub-class to accumulate
		some kind of summary.  Here, it is used to keep track of parameter
		means and standard deviations.
		"""
		Archive.__init__(self, lop, np_eff, strategy=strategy,
					maxArchSize=maxArchSize, alpha=alpha)
		self.p0 = lop[-1].vec()
		self.s = numpy.zeros(self.p0.shape, numpy.float)
		self.ss = numpy.zeros(self.p0.shape, numpy.float)
		for a in lop:
			self.append_hook(a)


	def append_hook(self, x):
		"""This accumulates parameter means and standard deviations.
		"""
		tmp = x.vec() - self.p0
		numpy.add(self.s, tmp, self.s)
		numpy.add(self.ss, numpy.square(tmp), self.ss)


	def truncate_hook(self, to_be_dropped):
		if len(to_be_dropped) > len(self.lop):
			# Take the opportunity to pick a better value of self.p0.
			self.p0 = self.s/(len(to_be_dropped) + len(self.lop))
			self.s = numpy.zeros(self.p0.shape)
			self.ss = numpy.zeros(self.p0.shape)
			for prms in self.lop:
				self.append_hook(prms)
		else:
			for prms in to_be_dropped:
				tmp = prms.vec() - self.p0
				numpy.subtract(self.s, tmp, self.s)
				numpy.subtract(self.ss, numpy.square(tmp), self.ss)

	def variance(self):
		with self.lock:
			n = len(self.lop)
			core = self.ss - self.s*self.s/n
			if not numpy.alltrue(numpy.greater(core, 0.0)):
				self.ss -= numpy.minimum(0.0, core)
				if Debug > 0:
					die.warn('Zero stdev in archive.stdev for p=%s'
							% ','.join( ['%d' % q for q
								in numpy.nonzero(numpy.less_equal(core, 0.0))[0]
							])
						)
				return numpy.ones(self.s.shape, numpy.float)
		assert n > 1
		assert numpy.alltrue(numpy.greater(core, 0.0))
		return core/(n-1)


class BootStepper(stepper):
	#: Targeted step acceptance rate.  This is from G. O. Roberts,
	#: A. Gelman, and W. Gilks (1997) "Weak convergence and optimal
	#: scaling of random walk Metropolis algorithm."  Ann.  Applied.
	#: Probability, 7, p. 110-120 and  also from
	#: G. O. Roberts and J. S. Rosenthal (2001) "Optimal scaling of
	#: various Metropolis-Hastings algorithms."  Statistical Sci.
	#: 16, pp. 351-367.
	F = 0.234
	#:  How rapidly should one expand the archive after a reset?
	alpha = 0.1
	#: Limits the probability of taking a bootstrap step.
	#: This, if the optimization collapses into a subspace, some other kind of step
	#: will eventually get it out.
	PBootLim = 0.9
	#: Control of when to sort steps and when to run with honest Monte-Carlo:
	SSAMPLE = ContPrmArchive.SSAMPLE	# Sampling mode
	SUPHILL = ContPrmArchive.SUPHILL	# Go straight uphill
	SANNEAL = ContPrmArchive.SANNEAL	# Simulated annealing
	SSAUTO = SANNEAL
	SSNEVER = SSAMPLE
	SSLOW = SANNEAL
	SSALWAYS = SUPHILL

	def __init__(self, lop, v, strategy=SANNEAL, maxArchSize=None, parallelSizeDiv=1):
		"""@param maxArchSize: How many position vectors can be stored.  This is
			normally used to (loosely) enforce a memory limitation for large
			jobs.
		@param parallelSizeDiv: For use when there are several cooperating MCMC
			processes that share data.  When >1, this allows each process
			to have smaller stored lists.   Normally, parallelSizeDiv is
			between 1 and the number of cooperating processes.
		"""
		stepper.__init__(self)
		_check_list_of_positions(lop)
		stepper._set_current(self, lop[-1])
		self.np = lop[0].vec().shape[0] #: The number of parameters:
		self.np_eff = (self.np+parallelSizeDiv-1)//parallelSizeDiv
		"""In a multiprocessor situation, np_eff tells you how much data do you
		need to store locally, so that the overall group of processors
		stores enough variety of data."""

		self.archive = ContPrmArchive(lop, self.np_eff, strategy=strategy,
						maxArchSize=maxArchSize, alpha=self.alpha)
		self.maxdups = int(round(4.0/self.F))

		if not self.np > 0:
			raise ValueError, "Np=%d; it must be positive." % self.np
		if v.shape != (self.np, self.np):
			raise ValueError, "v must be square, with side equal to the number of parameters. Vs=%s, np=%d." % (str(v.shape), self.np)

		self.v = numpy.array(v, numpy.float, copy=True)
		self.V = MVN.multivariate_normal(numpy.zeros(v.shape[0], numpy.float),
								v)
		self.aB = adjuster(self.F, vscale=0.5, vse=0.5, vsmax=1.3)
		self.aV = adjuster(self.F, vscale=1.0)
		self.steptype = None


	def step(self):
		stepper.step(self)
		WBoot = max(self.archive.distinct_count()-1, 0)
		WV = self.np_eff
		P = min(self.PBootLim, WBoot/float(WBoot+WV))
		if random.random() < P:
			try:
				accepted = self.step_boot()
			except NoBoot:
				accepted = self.stepV()
		else:
			accepted = self.stepV()
		return accepted




	# def prmlist(self):
		# return self.archive.prmlist()

	# def last(self):
		# return self.archive.last()
		
	
	def status(self):
		with self.lock:
			o = ['a0vs=%g' % self.aB.vscale,
				'a0acc=%g; a0try=%g; a0state=%d' % self.aB.status(),
				'a1vs=%g' % self.aV.vscale,
				'a1acc=%g;  a1try=%g; a1state=%d' % self.aV.status(),
				'nboot=%d' % len(self.archive),
				'logP=%g' % self.current().logp_nocompute(),
				'type=%s' % self.steptype
				]
		return '; '.join(o) + ';'


	def stepV(self):
		self.steptype = 'stepV'
		vs1 = self.aV.vs()
		move = self.V.sample() * vs1
		if hasattr(self.archive, 'variance') and self.archive.distinct_count() >= min(5, self.np):
			move *= (self.archive.variance()/self.v.diagonal())**0.25

		# print "self.current()=", self.current()
		try:
			tmp = self.current().new(move)
			delta = tmp.logp() - self.current().logp()
		except ValueError, x:
			die.warn('Cache trouble!: %s' % str(x))
			print 'current=', self.current()
			raise
		except NotGoodPosition, x:
			if Debug>2:
				die.warn('StepV: %s' % str(x))
			# Should I call self.aV.inctry(0) ?
			return 0
		if self.acceptable(delta):
			accepted = 1
			if Debug>2:
				die.info('StepV: Accepted logp=%g' % tmp.logp_nocompute())
			# We cannot use self.lop[-1] for current because lop is
			# sometimes sorted.  When it is, the most recently added
			# position could end up anywhere in the list.   Thus, we keep
			# a separate self._current.
			self._set_current(tmp)
			self.aV.inctry(accepted)
		else:
			self._set_failed( tmp )
			accepted = 0
			if Debug>2:
				die.info('StepV: Rejected logp=%g vs. %g, T=%g'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T()))
			self.aV.inctry(accepted)
			self._set_current(self.current())
		return accepted


	def step_boot(self):
		self.steptype = 'step_boot'
		vs0 = self.aB.vs()
		assert vs0 < 10.0, "Vs0 too big!=%s" % str(vs0)
		if Debug>3:
			die.note('VsB', vs0)

		if len(self.archive) <= 2:
			# print 'NoBoot', len(self.archive)
			raise NoBoot, "Cannot find bootstrap points"
		p1 = self.archive.choose()
		p2 = self.archive.choose()
		# if p1 is p2:
		if p1.uid() == p2.uid():
			# print 'NoBoot dup'
			raise NoBoot, "Bootstrap: Duplicate uid"

		# die.note('p1.prms', p1.prms())
		# die.note('p2.prms', p2.prms())
		move  = (p1.vec() - p2.vec()) * vs0
		# print '# move=', p1.prms(), p2.prms(), vs0, move

		try:
			tmp = self.current().new(move)
			delta = tmp.logp() - self.current().logp()
		except ValueError, x:
			die.warn('Cache trouble!: %s' % str(x))
			print 'current=', self.current()
			raise
		except NotGoodPosition:
			if Debug>2:
				die.warn('StepBoot: Nogood position')
			return 0
		if self.acceptable(delta):
			accepted = 1
			if Debug>2:
				die.info('StepBoot: Accepted logp=%g' % tmp.logp_nocompute())
			self._set_current(tmp)
			self.aB.inctry(accepted)
		else:
			self._set_failed( tmp )
			accepted = 0
			if Debug>2:
				die.info('StepBoot: Rejected logp=%g vs. %g, T=%g'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T()))
			self.aB.inctry(accepted)
			self._set_current(self.current())
		return accepted



	def _set_current(self, newcurrent):
		"""@raise NotGoodPosition: if newcurrent doesn't have a finite logp() value.
		"""
		g_implements.check(newcurrent, position_base)
		# print 'bootstepper.set_current', threading.currentThread().getName()
		stepper._set_current(self, newcurrent)
		out = []
		with self.lock:
			maxdups = self.maxdups if self.since_last_rst < self.np_eff else -1
			"""After a reset, the optimizer may not have good step directions,
			so there may be many failed steps.   Thus, you don't want to
			fill up the archive with lots of duplicates of the current position
			that are basically meaningless.    Thus, we forbid duplicates for
			a while."""

			q = self.archive.append(newcurrent, maxdups=maxdups)
			out.append(q)
			if self.needs_a_reset():
				# Shorten the archive -- if we've found a new best
				# point, that makes it likely that we have not
				# yet converged.   Consequently, since were
				# probably not near stationarity, the old history
				# is probably useless.
				self.reset_adjusters()
				self.archive.reset()
				self.reset()
				out.append('r')
		return ''.join(out)


	def _set_failed(self, f):
		"""We remember this failure for error reporting purposes.
		But, just because a step failed doesn't mean it is awful.   If the archive is
		sorted (i.e. we are in optimization mode, not sampling mode) and
		if the failed step is better than most of the archive, then remember it.
		"""
		stepper._set_failed(self, f)
		with self.lock:
			refPos = len(self.archive)//4
			try:
				if (f is not None
					and self.archive.sorted
					and f.logp_nocompute()>self.archive.lop[refPos].logp_nocompute()):
					self.archive.append(f, 1)
			except NotGoodPosition:
				pass


	def reset_adjusters(self):
		self.aB.reset()
		self.aV.reset()


	def ergodic(self):
		"""A crude measure of how ergodic the MCMC is.
		@return: The inverse of how many steps it takes to cross the
			minimum in the slowest direction.  Or zero, if it is too
			soon after some major violation of the MCMC assumptions.
		"""
		if self.since_last_rst*self.aB.f() < 3*self.np_eff:
			# Presumably, we are still stabilizing.   The factor of 3
			# is there to make sure that we have stopped sorting the archive.
			# (See Archive.sorted}.
			return 0.0
		if self.aB.state < 0:
			# The step size is known to be mis-adjusted,
			# so you cannot use it to compute a measure
			# of the ergodicity.
			# print '# state<0 in ergodic', self.aB.state
			return 0.0

		# This is calibrated from the equilibrium vscale from long runs
		# in 1-50 dimensional Gaussian problems.

		vsbar = 1.7/math.sqrt(self.np)	# Should this be np_eff ?
		vs = self.aB.vscale
		# print 'ergodic: vs=', vs, "erg=", min(1.0, vs/vsbar)**2
		return self.F * min(1.0, vs/vsbar) ** 2


	def set_strategy(self, ss):
		tmp = self.archive.strategy
		self.archive.strategy = ss
		return tmp

	set_sort_strategy = set_strategy


def bootstepper(logp, x, v, c=None, strategy=BootStepper.SANNEAL, fixer=None, repeatable=True):
	"""This is (essentially) another interface to the class constructor.
	It's really there for backwards compatibility.
	"""
	pd = problem_definition_F(logp_fcn=logp, c=c, fixer=fixer)
	position_constructor = [position_nonrepeatable, position_repeatable][repeatable]
	return BootStepper(make_list_of_positions(x, position_constructor, pd), v, strategy=strategy)

# boot2stepper = bootstepper

def _logp1(x, c):
	# print "x=", x, "c=", c
	# print "type=", type(x), type(c)
	return -numpy.sum(x*x*c*c)


def _logp2(x, c):
	r = numpy.identity(x.vec().shape[0], numpy.float)
	r[0,0] = 0.707107
	r[0,1] = 0.707107
	r[1,0] = -0.707107
	r[1,1] = 0.707107
	xt = numpy.dot(x, r)
	return _logp1(xt, c)


def test(stepper):
	import dictops
	start = numpy.array([1.0, 2.0, 2, 9, 1])
	c = numpy.array([100.0, 30.0, 10.0, 3.0, 0.1])
	V = numpy.identity(len(c), numpy.float)
	# V = numpy.array([[ 20.69626808,  20.6904984 ], [ 20.6904984,   20.69477235]])

	x = stepper(_logp1, start, V, c=c)
	v = numpy.zeros((x.np, x.np))
	n_per_steptype = dictops.dict_of_averages()
	for i in range(1000):
		accepted = x.step()
		n_per_steptype.add(x.steptype, accepted)
	lpsum = 0.0
	lps2 = 0.0
	na = 0
	psum = numpy.zeros((x.np,))
	N = 30000
	nreset = 0
	nsorted = 0
	rid = x.reset_id()
	for i in range(N):
		accepted = x.step()
		na += accepted
		n_per_steptype.add(x.steptype, accepted)
		nsorted += x.archive.sorted
		if x.reset_id() != rid:
			rid = x.reset_id()
			nreset += 1
		lp = x.current().logp()
		lpsum += lp
		lps2 += lp**2
		p = x.current().vec()
		numpy.add(psum, p, psum)
		v += numpy.outer(p, p)
	for steptype in n_per_steptype.keys():
		print 'Step %s has %.0f successes out of %.0f trials: %.2f' % (
			steptype, n_per_steptype.get_both(steptype)[0],
			n_per_steptype.get_both(steptype)[1],
			n_per_steptype.get_avg(steptype)
			)
	# assert N*x.PBootLim**1.5 < nboot < N*x.PBootLim**0.7
	assert nsorted < N//30
	assert N//8 < na < N//2
	assert nreset < 3
	lpsum /= N
	assert abs(lpsum+0.5*x.np) < 0.15, "Lpsum=%g, expected value=%g" % (lpsum, -0.5*x.np)
	lps2 /= N-1
	lpvar = lps2 - lpsum**2
	assert abs(lpvar-0.5*x.np) < 1.0
	numpy.divide(psum, N, psum)
	assert numpy.alltrue(numpy.less(numpy.absolute(psum), 6.0/numpy.sqrt(c)))
	numpy.divide(v, N-1, v)
	for i in range(x.np):
		for j in range(x.np):
			if i == j:
				# print '2*v[ii]*c=', 2*v[i,j]*c[i]**2
				assert abs(math.log(2*v[i,j]*c[i]*c[j])) < 0.1
			else:
				assert abs(v[i,j]) < 20/(c[i]*c[j])



def diag_variance(start):
	"""Hand this a list of vectors and it will compute
	the variance of each component, then return a diagonal
	covariance matrix.
	"""
	tmp = gpkmisc.vec_variance(start)
	if not numpy.alltrue(numpy.greater(tmp, 0.0)):
		raise ValueError, ("Zero variance for components %s"
					% ','.join(['%d'%q for q in
							numpy.nonzero(1-numpy.greater(tmp, 0.0))[0]
						]
						)
					)
	return gpkmisc.make_diag(tmp)




if __name__ == '__main__':
	test(stepper=bootstepper)
