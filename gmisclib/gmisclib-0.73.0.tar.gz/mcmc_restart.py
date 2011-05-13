import cPickle

import die
import mcmc

import mcmc_indexclass as IC
import mcmc_newlogger as LGI




def setup(pd_factory, arglist, uid='UID'):
	"""This and prepares to restart a mcmc.py optimization
	from a log file.
	@param arglist: the list of arguments to the optimization routine (i.e. the linux command line).
	@type arglist: list(str)
	@note: This assumes that an optimization does not require any
		fixed parameters.
	"""
	argliste = None
	idxrs = []
	hdrs = {}
	while arglist and arglist[0]=='-restart':
		assert len(arglist)>=2

		hdr, indexers, logps = LGI.read_multi_uid(arglist[1], uid, Nsamp=-1)
		idxrs.extend(indexers)
		hdrs.update(hdr)
		argliste = cPickle.loads(hdr['Argv']) + arglist[2:]
		arglist = arglist[2:]

	if argliste is None:
		argliste = list(arglist)
		olov = []
		indexers = []

	pd = pd_factory(list(argliste), hdrs)
	guess = IC.guess(pd.PriorProbDist)
		# This is deferred initialization for problem_def:
	tries = 0
	while True:
		try:
			pd.logp_guts(guess)
		except mcmc.NotGoodPosition:
			die.warn("Initial position is not good.%s" % (('', '  Will try again.')[tries+1<6]))
			tries += 1
		else:
			break
		if tries > 20:
			die.die("Cannot find a good starting parameter in %d tries." % tries)
	die.info("Adjustable parameters: %s" % ' '.join(guess.columns()))
	pd.set_idxr( IC.guess_to_indexer(guess) )
	olov = [IC.reindex(q, pd.idxr).get_prms() for q in indexers]
	# ...at this point, we have lost the fixed parameters.

	def lov_gen(olov, guess):
		"""Guess some initial values to seed the iteration."""
		for v in olov:
			yield v
		while True:
			yield guess.get_prms()

	return (argliste, pd, lov_gen(olov, guess), len(olov))

