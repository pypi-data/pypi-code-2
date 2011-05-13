
"""An extension of mcmc that includes new stepping algorithms.
"""

from __future__ import with_statement

import math
import random
import numpy

import die
import mcmc
import avio
from mcmc import Debug
import gpk_lsq

SIGFAC = 2.0

NotGoodPosition = mcmc.NotGoodPosition

def N_maximum(a):
	return a[numpy.argmax(a)].item()

def _parab_interp_guts(x0, y0, x1, y1, x2, y2):
	xx01 = x0**2 - x1**2
	x01 = x0 - x1
	y01 = y0 - y1
	xx21 = x2**2 - x1**2
	x21 = x2 - x1
	y21 = y2 - y1
	
	b = (y01*xx21 - y21*xx01) / (xx21*x01 - xx01*x21) 
	a = (y01 - b*x01) / xx01
	c = y0 - a*x0**2 - b*x0
	return (a, b, c)


def pairmax(*xy):
	"""Finds the (x,y) pair which has the largest y."""
	bestx, besty = xy[0]
	for (x,y) in xy[1:]:
		if y > besty:
			besty = y
			bestx = x
	return (bestx, besty)


def _parab_interp(x0, y0, x1, y1, x2, y2):
	xctr = (x0 + x1 + x2) / 3.0
	# print 'XY=', (x0, y0), (x1, y1), (x2, y2)
	x0 -= xctr
	x1 -= xctr
	x2 -= xctr

	# print 'xy=', (x0, y0), (x1, y1), (x2, y2)
	a, b, c = _parab_interp_guts(x0, y0, x1, y1, x2, y2)
	# print 'abc=', a, b, c
	mn = min(x0, x1, x2)
	mx = max(x0, x1, x2)
	w = mx - mn
	if a >= 0.0:
		raise mcmc.NoBoot, "parab: positive curvature"
	else:
		# This looks like a nice parabola with a maximum.   We step
		# into the vicinity of the maximum.
		xmin = -b/(2*a)
		sigma = math.sqrt(-SIGFAC/(2*a))

	TOOCLOSE = 0.02
	TOOFAR = 2.0
	if xmin < -TOOFAR*w:
		xmin = -TOOFAR*w
	elif xmin > TOOFAR*w:
		xmin = TOOFAR*w
	if sigma > TOOFAR*w:
		sigma = TOOFAR*w
	elif sigma < 2*TOOCLOSE*w:
		sigma = 2*TOOCLOSE*w

	xtmp = random.normalvariate(xmin, sigma)
	while min(abs(xtmp-x0), abs(xtmp-x1), abs(xtmp-x2)) < TOOCLOSE*w:
		xtmp = random.normalvariate(xtmp, sigma)
		# The minimum is too nearly a replication of an existing point,
		# so we try again to make sure we get some new information.
	return xctr + xtmp


def test():
	a, b, c = _parab_interp_guts(0.0, 1.0, 1.0, 0.0, 2.0, 1.0)
	assert abs(a-1.0) < 0.001
	assert abs(-b/(2*a) - 1.0) < 0.001
	assert abs(c-1.0) < 0.001



def find_closest_p(v, *vp):
	"""Searches a list of (v,p) pairs and finds the one whose v
	is closest to the first argument.   Returns
	(v,p) of the closest pair.
	"""
	assert len(vp) > 0
	vc, pc = vp[0]
	for (vi, pi) in vp[1:]:
		if abs(vi-v) < abs(vc-v):
			vc = vi
			pc = pi
	return (vc, pc)


# class multiD_history(object):
	# def __init__(self):
		# self.uids = frozenset()
		# self.n = 0
# 	
	# def mode(self, uids):
		# fs = frozenset(uids)
		# if fs == self.uids:
			# self.n += 1
		# else:
			# self.n = 0
			# self.uids = fs
		# return self.n
# 


def _fast_adjust(moveB, moveV, VFAC, aV, aB, accepted):
	"""@note: this breaks the Markov assumption."""
	# If the moveB completely dominates moveV, then we can apply our knowledge of
	# whether the step was accepted or not to adjusting the size of the Bootstrap step.
	if numpy.greater(numpy.absolute(moveB), numpy.absolute(moveV)).all():
		aB.inctry(accepted)
	# Adjust the stepV step size to approximately match the stepBoot step size.
	SLOP = 5.0
	if numpy.greater(numpy.absolute(moveB), SLOP*numpy.absolute(moveV)/VFAC).all():
		aV.inctry(0)
	if numpy.greater(numpy.absolute(moveV)/VFAC, SLOP*numpy.absolute(moveB)).all():
		if random.random():
			aV.inctry(1)


class BootStepper(mcmc.BootStepper):
	def __init__(self, lop, v, strategy=mcmc.BootStepper.SSAUTO,
				maxArchSize=None, parallelSizeDiv=1):
		mcmc.BootStepper.__init__(self, lop, v, strategy=strategy,
						maxArchSize=maxArchSize,
						parallelSizeDiv=parallelSizeDiv)
		# self.multiD_hist = multiD_history()


	def step(self):
		mcmc.stepper.step(self)
		Wboot = max(self.archive.distinct_count()-2, 0)
		WV = self.np
		Wmixed = math.sqrt(Wboot * WV)
		# Parabolic steps are a bootstrap method, so they needs a large archive.
		# But, Step_parab is not really Markov, so we only want to do it 
		# to help find the minimum after a reset.
		die.info("STEP: sorted=%s strategy=%s" % (self.archive.sorted, self.archive.strategy))
		# if self.archive.strategy != self.archive.SSAMPLE:
		# else:
		if self.archive.sorted:
			Wparab = max(self.archive.distinct_count()-2, 0)
		else:
			Wparab = 0
		if self.np<30 and (self.archive.sorted or self.archive.strategy!=self.SSAMPLE):
			WmultiD = math.sqrt(max(self.archive.distinct_count()-(self.np+1), 0) * WV)
		else:
			WmultiD = 0
		W = float(Wboot + Wmixed + Wparab + WV + WmultiD)
		Pboot = Wboot/W
		Pmixed = Pboot + Wmixed/W
		Pparab = Pmixed + Wparab/W
		PmultiD = Pparab + WmultiD/W

		again = True
		while again:
			P = random.random()
			try:
				if P < Pboot:
					accepted = self.step_boot()
				elif P < Pmixed:
					accepted = self.step_mixed()
				elif P < Pparab:
					# Note! This violates MCMC requirements!
					# The resulting probability distribution will not be correct
					# when step_parab() is used!
					accepted = self.step_parab()
				elif P < PmultiD:
					# Note! This violates MCMC requirements!
					# The resulting probability distribution will not be correct
					# when step_multiD() is used!
					accepted = self.step_multiD()
				else:
					accepted = self.stepV()
			except mcmc.NoBoot, x:
				die.info('NoBoot: %s' % str(x))
				again = True
			else:
				again = False
		return accepted


	def step_mixed(self):
		VFAC = 0.01
		self.steptype = 'step_mixed'
		if len(self.archive) <= 2:
			# print 'NoBoot', len(self.archive)
			raise mcmc.NoBoot, "mixed short archive"
		p1 = self.archive.choose()
		p2 = self.archive.choose()
		if p1.uid() == p2.uid():
			# print 'NoBoot dup'
			raise mcmc.NoBoot, "mixed duplicate"

		vsV = self.aV.vs() * VFAC
		if self.archive.distinct_count() >= min(5, self.np_eff):
			vsV *= (self.archive.variance()/self.v.diagonal())**(1./4.)

		moveB  = (p1.vec() - p2.vec()) * self.aB.vs()
		moveV  = vsV * VFAC * self.V.sample()
		move = moveB + moveV
		try:
			tmp = self.current().new(move)
			delta = tmp.logp() - self.current().logp()
		except mcmc.NotGoodPosition:
			die.warn('NotGoodPosition')
			# Should I call self.aM.inctry(accepted) ?
			return 0
		if self.acceptable(delta):
			accepted = 1
			self._set_current(tmp)
			if Debug>2:
				die.info('StepMixed: Accepted logp=%g' % tmp.logp_nocompute())
		else:
			self._set_failed( tmp )
			accepted = 0
			self._set_current(self.current())
			if Debug>2:
				die.info('StepMixed: Rejected logp=%g vs. %g, T=%g'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T()))

		# Only do this after a reset or when we don't care about breaking Markov assumptions:
		if self.archive.sorted:
			_fast_adjust(moveB, moveV, VFAC, self.aV, self.aB, accepted)
		return accepted



	def step_parab(self):
		VFAC = 0.01
		self.steptype = 'step_parab'
		# The parabolic fit will be degenerate if we pick vs0 too close
		# to either of the existing points.
		if len(self.archive) <= 2:
			raise mcmc.NoBoot, "parab short archive"
		vsB = self.aB.vs()
		while True:
			vs0 = random.normalvariate(0.0, vsB)
			# Don't pick a point too close to the existing points.
			if abs(vs0)>vsB/4.0 and abs(vs0-1)>vsB/4.0:
				break

		p1 = self.current()
		p2 = self.archive.choose()
		if p1.uid() == p2.uid():
			raise mcmc.NoBoot, "parab duplicate"

		vbase, pbase = find_closest_p(vs0, (0.0, p1), (1.0, p2))
		move  = (p2.vec() - p1.vec()) * (vs0-vbase)
		# This is a perfectly good MCMC step, at least when the
		# archive is large and well-annealed.
		try:
			tmp = pbase.new(move)
			delta = tmp.logp() - self.current().logp()
		except mcmc.NotGoodPosition:
			die.warn('NotGoodPosition2a at %.3f' % vs0)
			return 0
		if self.acceptable(delta):
			if Debug > 2:
				die.info('StepParab Accepted1 at %.3f, logp=%g' % (vs0, tmp.logp_nocompute()))
			self._set_current(tmp)
		else:
			self._set_failed( tmp )
			self._set_current(self.current())
			# Return from here?  No.  It still can be used to
			# define the interpolation parabola, even if logP
			# isn't particularly good.

		try:
			vsnew = _parab_interp(0.0, p1.logp(), 1.0, p2.logp(), vs0, tmp.logp())
		except mcmc.NotGoodPosition:
			die.warn('NotGoodPosition preparing for _parab_interp().')
			return 0
		vbase, pbase = find_closest_p(vsnew, (0.0, p1), (1.0, p2), (vs0, tmp))
		moveP  = (p2.vec() - p1.vec()) * (vsnew-vbase)

		# Some of the time, we add in a bit of stepV, to make sure we escape
		# from any subspace we might have gotten trapped in...
		if random.random() < 0.5:
			moveV = self.aV.vs() * VFAC * self.V.sample()
			move = moveP + moveV
		else:
			move = moveP
			moveV = None

		try:
			tmp = pbase.new(move)
			delta = tmp.logp() - self.current().logp()
		except mcmc.NotGoodPosition:
			die.warn('NotGoodPosition')
			accepted = 0
		if self.acceptable(delta):
			if Debug > 2:
				die.info('StepParab Accepted2 at %.3f, logp=%g' % (vsnew, tmp.logp_nocompute()))
			accepted = 1
			self._set_current(tmp)
		else:
			self._set_failed( tmp )
			accepted = 0
			self._set_current(self.current())
			if Debug>2:
				die.info('StepParab: Rejected logp=%g vs. %g, T=%g'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T()))
		# These lines seem to make it worse:
		# if accepted and moveV is not None:
			# _cross_adjust(moveP, moveV, VFAC, self.aV)
		return accepted


	def step_multiD(self):
		self.steptype = 'step_multiD'
		if self.archive.distinct_count() <= self.np + 2:
			raise mcmc.NoBoot, "multiD: archive length too small: %d vs np=%d" % (len(self.archive), self.np)

		# n_w_distinct = int(round(
		# 			((self.np*(self.np+1))//2 + self.np + 1)
		# 			* float(len(self.archive))/float(self.archive.distinct_count())
		# 			))
		n_w_distinct = 2*self.np
		lop = self.archive.prmlist(n_w_distinct)
		n = 0
		lolp = []
		lop2 = []

		# unique = set()
		z0 = self.current().logp()
		x0 = self.current().vec()
		# for p in lop:
			# unique.add(p.uid())
		# if len(unique) <= 1 + self.np + self.np//4:
			# raise mcmc.NoBoot, "multiD: N(unique) too small: %d vs np=%d" % (len(unique), self.np)
		# mode = self.multiD_hist.mode(unique)
		vs = numpy.zeros(lop[0].vec().shape)
		n = 0
		lolp = []
		lop2 = []
		for p in lop:
			try:
				lolp.append(p.logp())
				numpy.add(vs, (p.vec()-x0)**2, vs)
				lop2.append(p.vec())
				n += 1
			except mcmc.NotGoodPosition:
				pass
		sigx = numpy.sqrt(vs/(n-1))
		if numpy.less(sigx, 1e-30).any():
			raise mcmc.NoBoot, "multiD: sigx too small = %s" % str(sigx)
		sz = 0.0
		for lp in lolp:
			sz += abs(z0 - lp)
		sigz = sz/(n-1)
		if sigz < 0.25 * self.acceptable.T():
			raise mcmc.NoBoot, "multiD: sigz too small = %g" % sigz
		# print 'x0=', x0, 'sigx=', sigx

		width = 1 + self.np + (self.np*(1+self.np))//2
		y = numpy.zeros((len(lolp), 1))
		a = numpy.zeros((len(lolp), width))
		# Order of parameter is a is Constant, linear slopes, then quadratic coefficients.
		for (i, (p, lp)) in enumerate(zip(lop2, lolp)):
			y[i,0] = z0 - lp
			pt = (p-x0)/sigx
			a[i,0] = 1.0
			a[i,1:1+self.np] = pt
			_unfold(pt, a[i,1+self.np:])

		rfactors = None
		nbe = None
		for tries in range(5):
			nbe = None
			try:
				move, rfactors = self._compute_move(a, y, width, x0, sigx)
			except mcmc.NoBoot, nbe:
				pass
			else:
				break
		if nbe:
			raise nbe
		die.info("stepMultiD: plausible step on try %d" % tries)

		try:
			tmp = self.current().new(move)
			delta = tmp.logp() - self.current().logp()
		except mcmc.NotGoodPosition:
			die.warn('NotGoodPosition')
			return 0
		if self.acceptable(delta):
			accepted = 1
			self._set_current(tmp)
			if Debug>2:
				die.info('StepMultiD: Accepted logp=%g; %s' % (tmp.logp_nocompute(), avio.concoct(rfactors)))
		else:
			self._set_failed( tmp )
			accepted = 0
			self._set_current(self.current())
			if Debug>2:
				die.info('StepMultiD: Rejected logp=%g; was=%g; T=%g; %s'
						% (tmp.logp_nocompute(), self.current().logp_nocompute(), self.acceptable.T(),
							avio.concoct(rfactors)))
		return accepted

	def _compute_move(self, a, y, width, x0, sigx):
		FARSTEP = 4.0
		rscale = math.exp(-random.expovariate(0.2))
		regstr, regtgt, rfactors = _regularize(self.np)
		rfactors['rscale'] = rscale
		lls = gpk_lsq.reg_linear_least_squares(a, y, regstr=regstr, regtgt=regtgt, rscale=rscale, copy=False)
		try:
			sv = lls.sv_reg()
			x = lls.x()
		except numpy.linalg.linalg.LinAlgError, ex:
			raise mcmc.NoBoot, "multiD: %s in _compute_move" % str(ex)
		assert x.shape == (width,1), "shape=%s" % str(x.shape)
		c = x[1:1+self.np, 0]
		cc = _refold(x[1+self.np:,0], self.np)
		# print 'c=', c
		# print 'cc=', cc
		if sv[-1] < 1e-6*sv[0]:
			raise mcmc.NoBoot, "Sv ratio too extreme: %g/%g" % (sv[-1], sv[0])
		move = _pick_min(c, cc, self.acceptable.T())*sigx + x0 - self.current().vec()
		r = N_maximum(numpy.absolute(move)/sigx)
		die.info('multiD move= %s (r=%.3f) from %s' % (move, r, self.current().vec()))
		if r > FARSTEP**2:
			raise mcmc.NoBoot, "multiD: unreasonably large step: r=%g" % r
		elif r > FARSTEP:
			numpy.multiply(move, (FARSTEP/r)**2, move)
		return (move, rfactors)


def _unfold(p, rv):
	n = (p.shape[0]*(p.shape[0]+1))//2
	assert rv.shape == (n,)
	k = 0
	for i in range(p.shape[0]):
		for j in range(p.shape[0]):
			if i <= j:
				rv[k] = p[i]*p[j]
				k += 1
	assert k == n


def _refold(m, n):
	assert len(m.shape)==1
	assert (n*(n+1))//2 == m.shape[0]
	rv = numpy.zeros((n, n))
	k = 0
	for i in range(n):
		for j in range(n):
			if i <= j:
				rv[i,j] = m[k]
				rv[j,i] = m[k]
				k += 1
	return rv

	
def _regularize(n):
	"""This weakly constrains the diagonal elements (the curvatures) to be equal,
	and it more strongly constrains the off-diagonal elements to be zero.
	"""
	FORCE_SIMILAR = math.exp(random.normalvariate(-4.0, 3.0))

	m = (n*(n+1))//2
	sz = 1 + n + m
	regtgt = numpy.zeros((sz, 1))
	regstr = numpy.zeros((sz, sz))
	diag = []
	k = 1 + n
	for i in range(n):
		for j in range(n):
			if i <= j:
				if i == j:
					regstr[k, k] = FORCE_SIMILAR
					diag.append(k)
				else:
					regstr[k, k] = 1.0
				k += 1
	lmbda = math.exp(random.expovariate(2.0))
	for k1 in diag:
		regtgt[k1,0] = lmbda
		for k2 in diag:
			regstr[k1,k2] = -FORCE_SIMILAR
			regstr[k2,k1] = -FORCE_SIMILAR
	return (regstr, regtgt, {'FORCE_SIMILAR': FORCE_SIMILAR, 'lmbda': lmbda})


def _pick_min(c, cc, T):
	rv = -0.5 * numpy.linalg.tensorsolve(cc, c)
	dzds = numpy.dot(c, rv)
	curv = numpy.dot(numpy.dot(rv, cc), rv)
	if curv <= 0:
		raise mcmc.NoBoot, "multiD: Negative curvature"
	assert abs(-dzds/(2*curv) - 1) < 0.01
	sigma = math.sqrt(SIGFAC*T/(2*curv))
	rv *= random.normalvariate(1.0, sigma)
	return rv


def bootstepper(logp, x, v, c=None, strategy=BootStepper.SSAUTO, fixer=None, repeatable=True):
	"""This is (essentially) another interface to the class constructor.
	It's really there for backwards compatibility.
	"""
	pd = mcmc.problem_definition_F(logp_fcn=logp, c=c, fixer=fixer)
	position_constructor = [mcmc.position_nonrepeatable, mcmc.position_repeatable][repeatable]
	return BootStepper(mcmc.make_list_of_positions(x, position_constructor, pd), v, strategy=strategy)

diag_variance = mcmc.diag_variance
stepper = mcmc.stepper
problem_definition = mcmc.problem_definition
problem_definition_F = mcmc.problem_definition_F
problem_definition = mcmc.problem_definition
position_repeatable = mcmc.position_repeatable
position_nonrepeatable = mcmc.position_nonrepeatable
position_history_dependent = mcmc.position_history_dependent

def test2d(stepper):
	import dictops
	start = numpy.array([9, 1])
	c = numpy.array([1.0, 0.1])
	V = numpy.identity(len(c), numpy.float)
	# V = numpy.array([[ 20.69626808,  20.6904984 ], [ 20.6904984,   20.69477235]])

	x = stepper(mcmc._logp1, start, V, c=c)
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
	assert nreset < 30
	lpsum /= N
	assert abs(lpsum+0.5*x.np) < 0.15
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


if __name__ == '__main__':
	# mcmc.test(stepper=bootstepper)
	Debug = 3
	mcmc.test(stepper=bootstepper)
