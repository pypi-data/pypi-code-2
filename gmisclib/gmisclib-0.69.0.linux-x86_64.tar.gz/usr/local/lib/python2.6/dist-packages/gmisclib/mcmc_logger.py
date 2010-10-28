import re

import numpy

from gmisclib import die
from gmisclib import fiatio
from gmisclib import dictops
from gmisclib import gpkmisc
from gmisclib import nice_hash
from gmisclib import mcmc_helper as mcmcP


class WildNumber(ValueError):
        def __init__(self, *s):
                ValueError.__init__(self, *s)


class logger_c(mcmcP.logger_template):
	"""This class is called from the Markov-Chain stepper
	and writes the log file.
	"""
	def __init__(self, logwriter, iterstep=100, ergstep=0.1):
		assert iterstep >= 0
		assert ergstep >= 0.0
		# self.lg = LG.logger(fd)
		self.lg = logwriter
		self.iterstep = iterstep
		self.ergstep = ergstep
		# self.__g_implements__ = ['logger_template']
		self.nlogged = 0
		self.erg = 0.0
		self.last_add_iter = 0
		self.last_logged_erg = None
		self.last_logged_iter = None
		self.best = None
		self.reason = 'sampled'


	def set_logstep(self, iterstep, ergstep, reason='sampled'):
		self.reason = reason
		assert iterstep > 0
		self.iterstep = iterstep
		if ergstep is None:
			self.ergstep = 0.0
		else:
			assert ergstep >= 0.0
			self.ergstep = ergstep
		self.lg.flush()


	def add(self, stepperInstance, iter):
		"""Called every step: this decides whether
		data should be logged.
		"""
		self.erg += stepperInstance.ergodic() * (iter-self.last_add_iter)
		self.last_add_iter = iter
		reason = []
		if(self.last_logged_iter is None or self.last_logged_erg is None):
			reason.append('initial')
		elif(iter>self.last_logged_iter+self.iterstep
			and self.erg>self.last_logged_erg+self.ergstep
			):
			reason.append(self.reason)
		else:
			clp = stepperInstance.current().logp_nocompute()
			if self.best is None or clp>self.best:
				self.best = clp
				reason.append('best')
		if reason:
			self.Add(stepperInstance, iter, reason=','.join(reason))


	def Add(self, stepperInstance, iter, reason=None):
		raise RuntimeError, "Virtual Function"



	def close(self):
		self.lg.close()

	def comment(self, comment):
		self.lg.comment(comment)
		self.lg.flush()

	def header(self, k, v):
		self.lg.header(k, v)

	def headers(self, hdict):
		self.lg.headers(hdict)

	def reset(self):
		self.nlogged = 0
		self.erg = 0.0
		self.last_logged_erg = None
		self.comment("Reset")


	def set_trigger_point(self):
		self.nlogged = 0
		self.erg = 0.0
		self.last_logged_erg = None
		self.comment("run_to_bottom finished")




class logger_A(logger_c):
	def __init__(self, logwriter, iterstep=100, ergstep=0.1):
		"""logwriter is a fiatio.writer or avio.writer or similar instance.
		"""
		logger_c.__init__(self, logwriter, iterstep=iterstep, ergstep=ergstep)
		self.HUGEp = 1e10
		self.HUGEl = 1e10


	def ok_logp(self, logpval):
		return -self.HUGEl < logpval < self.HUGEl


	def ok_prms(self, prms):
		return numpy.greater_equal(self.HUGEp, prms) * numpy.greater_equal(prms, -self.HUGEp)


	def fmt(self, prmname):
		return ','.join(['%s' % q for q in prmname])


	def get_map(self, stepper):
		return stepper.current().pd.idxr.map


	def Add(self, stepperInstance, iter, reason=None):
		self.nlogged += 1
		self.last_logged_erg = self.erg
		self.last_logged_iter = iter
		prms = stepperInstance.current().prms()
		logp = stepperInstance.current().logp_nocompute(),
		tmp = {'T': stepperInstance.acceptable.T(),
			'resetid': stepperInstance.reset_id(),
			'iter': iter
			}
		if reason is not None:
			tmp['why_logged'] = reason
		wild = []
		if logp is None or not self.ok_logp(logp):
			tmp['logp'] = '%.2f' % logp
		else:
			wild.append("logp=%s" % str(logp))
		okprm = self.ok_prms(prms)
		map = self.get_map(stepperInstance)
		if not okprm.all():
			rmap = dictops.rev1to1(map)
			for (i,isok) in enumerate(okprm):
				if not isok:
					wild.append( 'p%d(%s)=%s' % (i, self.fmt(rmap[i]), prms[i]) )
		for (nm, i) in map.items():
			tmp['P.%s' % self.fmt(nm)] = prms[i]
		self.lg.datum(tmp)
		self.lg.flush()
		if wild:
			raise WildNumber, '; '.join(wild)




class logger_N(logger_c):
	def __init__(self, logwriter, iterstep=100, ergstep=0.1):
		"""logwriter is really a newstem2.newlogger instance.
		"""
		logger_c.__init__(self, logwriter, iterstep=iterstep, ergstep=ergstep)



        def Add(self, stepperInstance, iter, reason=None):
                """Actually write a set of parameters into the log file."""
                print 'Logging', stepperInstance.current().logp_nocompute(), 'iter=', iter
                self.nlogged += 1
                self.last_logged_erg = self.erg
                self.last_logged_iter = iter
                self.lg.add('UID', stepperInstance.current().prms(),
                                stepperInstance.current().pd.idxr.map,
                                stepperInstance.current().logp_nocompute(),
                                iter,
                                extra={'T': stepperInstance.acceptable.T(),
                                        'resetid': stepperInstance.reset_id(),
                                        },
                                reason=reason
                                )
                self.lg.flush()





BadFormatError = fiatio.BadFormatError

def _read_currentlist(fname, trigger=None):
	if trigger is not None:
		print '# Trigger="%s"' % trigger
		trigger = re.compile(trigger)
	currentlist = []
	lasthdr = {}
	lineno = 1
	for (hdr, data, comments) in fiatio.readiter(gpkmisc.open_compressed(fname)):
		if comments and trigger is not None:
			for c in comments:
				if trigger.match(c):
					print '# Trigger match'
					trigger = None
		if trigger is None and data is not None:
			data['__line'] = lineno
			currentlist.append( data )
		lasthdr.update(hdr)
		lineno += 1
	if trigger is not None:
		die.warn('Trigger set but never fired: %s' % fname)
	return (currentlist, lasthdr)


class lti_c(object):
	def __init__(self):
		self.h = nice_hash.simple()
		from newstem2 import indexclass
		self.IC = indexclass

	def parse(self, d):
		unfmt = self.IC.index_base._unfmt
		PREFIX = 'P.'
		lp = len(PREFIX)
		if not self.h.n:
			for (k, v) in d.items():
				if k.startswith(PREFIX):
					self.h.add(unfmt(k[lp:]))
		prms = numpy.zeros((self.h.n,))
		n = 0
		for (k, v) in d.items():
			if k.startswith(PREFIX):
				prms[self.h.get_image(unfmt(k[lp:]))] = float(v)
				n += 1
		if n < self.h.n:
			raise BadFormatError, "Missing parameter"
		return self.IC.index(self.h.map(), p=prms, name=d.get('uid'))



class NoDataError(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)



def read_multisample(fname, Nsamp=10, tail=0.0, trigger=None):
	"""Read in a log file: it gives you multiple samples
	from the log.   In other words, it provides a time-series of the changes
	to the parameters.

	@param tail: Where to start in the file?
		C{tail=0} means that you start at the trigger or beginning.
		C{tail=1-epsilon} means you take just the last tiny bit of the file.
	"""
	currentlist, lasthdr = _read_currentlist(fname, trigger=trigger)
	if len(currentlist) == 0:
		raise NoDataError, fname

	lc = len(currentlist)
	tail = min(tail, 1.0 - 0.5/lc)
	nsamp = min(Nsamp, lc-int(lc*tail))	# How many samples to extract?
	print '# len(currentlist)=', len(currentlist), 'tail=', tail, 'nsamp=', nsamp
	assert nsamp > 0
	lti = lti_c()
	indexers = []
	logps = []
	try:
		for i in range(nsamp):
			f = float(i)/float(nsamp)
			aCurrent = currentlist[int((tail + (1.0-tail)*f)*lc)]
			assert len(currentlist) > 0
			indexers.append( lti.parse(aCurrent) )
			logps.append( float(aCurrent['logp']) )
	except nice_hash.NotInHash, x:
		raise BadFormatError, "Unexpected parameter %s appearing on %s:%d"  % (x, aCurrent['__line'], fname)
	except BadFormatError, x:
		raise BadFormatError, "%s line %s:%d" % (x, aCurrent['__line'], fname)
	return (lasthdr, indexers, logps)
