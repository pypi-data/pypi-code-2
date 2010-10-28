"""Adaptive Markov-Chain Monte-Carlo algorithm.
This can be used to generate samples from a probability distribution,
or also as a simulated annealing algorithm for maximization.
This can be used as a script, from the command line, or (more likely)
it can be imported and its functions and classes can be used.

The central interfaces are the L{BootStepper} class, and within
it, the C{step()} method is used iteratively to take a Markov step.

To use it as a script, you create your own module that implements
a few functions, and run C{mcmc.py}.  It will import your module
and call your functions repeatedly.

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

As a script, it takes the following arguments:
	- C{-o fff}	Specifies a log file for some basic logging.

	- {C -py ddd/mm}	Specifies the module to load and to optimize.
		If the name contains a slash, it searches C{ddd}
		instead of the python search path, looking for a module
		named C{mm}.  If no slash, then it looks up the module
		in C{PYTHONPATH}.

	- C{-NI NN}	Sets the number of iterations.  Required, unless the
		module defines C{yourmod.NI}.

	- C{--}	Stops interpretation of the argument list.
		The remainder is passed to yourmod.init(), if
		it is defined, then to yourmod.start(), if that is
		defined.

It uses the following functions and variables:

	- C{yourmod.c}	(required).
		This is an object that is passed into C{yourmod.resid()}
		or C{yourmod.logp()}.  You can make it be anything you
		want, as it is only touched by your functions.
		Often, it contains data or parameters for these functions,
		but it can be L{None} if you have no need for it.

	- C{yourmod.start(arglist, c)}  (Not required).
		This is where you initialize the Monte-Carlo iteration.
		If you define yourmod.start(), it is passed the arglist,
		after the standard C{mcmc.py} flags and arguments are removed
		from it.   C{Yourmod.start()}
		must return a list of one or more starting vectors,
		(either a list of numpy arrays or a list of sequences
		of floats).    These starting vectors are used to seed the iteration.
		
		If it is not defined, mcmc.py will read a list
		of starting vectors in ascii format from the standard input
		using L{_read}().
		
	- C{yourmod.init(ndim, ni, c, arglist)}   (Not required).
		This is primarily there to open a log file.
		Init is passed the remainder of the scripts argument
		list, after yourmod.start() looks at it.    It can do anything
		it wishes with the argument list.  It can return an object or None.
		
		If it returns something other than L{None}, it will be used
		this way::

		x = yourmod.init(ndim, ni, yourmod.c, arglist)
		x.add(parameters, iteration)
		# add is there to accumulate averages of parameters
		# or to log parameter vectors.
		x.finish(sys.stdout)
		# finish can be used to print a summary or close a log file.

		C{Ndim} is the length of the parameter vector,
		C{ni} is the number of iterations, C{c} is C{yourmod.c}.

	- C{yourmod.resid(x, c)}  (Either yourmod.logp() or yourmod.resid() is required.)

	- C{yourmod.logp(x, c)}  (Either C{yourmod.logp} or C{yourmod.resid} is required.)
		These funtions are the thing which is to be optimized.
		C{Yourmod.log} returns the logarithm (base e) of the probability
		density at position C{x}.  (It does not need to be normalized, so it really
		only needs something proportional to the probability density.)
		C{X} is a numpy array (a 1-dimensional vector),
		and C{c} is an arbitrary object that you define.
		
		C{Yourmod.logp} should return L{None} if x is a silly value.  Either that,
		or it can raise a L{NotGoodPosition} exception.  Note that
		the optimizer will tend to increase values of logp.  It's a maximizer,
		not a minimizer!
		
		If you give yourmod.resid() instead, logp() will be calculated
		as -0.5 times the sum of the squares of the residuals.   It should
		return a numpy vector.  It may return None, or raise L{NotGoodPosition}, which will
		cause the optimizer to treat the position as extremely bad.

	- yourmod.log(result_of_init, i, p, w)   (Not required).
		This is basically a function to log your data.
		No return value.    It is called at every step and
		passed the result of yourmod.init() (which might
		be a file descriptor to write into).  It is also passed the iteration
		count, i, the current parameter vector, p, and w, which is reserved
		for possible future use.


	- yourmod.NI  (required unless the -NI argument is given on the command line)
		Specifies how many iterations.  This is an integer.

	- yourmod.STARTLOW (not required).  Integer 0 or 1.
		If true, the iteration is started from the largest value of logp
		that is known.


	- yourmod.V	(Not required)
		This specifies the covariance matrix that is used to hop from one
		test point to another.   It is
		a function that takes the result of yourmod.start() and returns
		a Numeric/numarray 2-dimensional square matrix,

		If it is not specified, mcmc will use some crude approximation
		and will probably start more slowly, but should work OK.
		If it is not specified and yourmod.start() returns only
		one starting position, then it will just use an identity matrix
		as the covariance matrix, and it might still work, but
		don't expect too much.
"""
from __future__ import with_statement

import sys

import numpy

from gmisclib import die
from gmisclib import mcmc
from gmisclib import gpkmisc
from gmisclib import g_implements
from gmisclib import multivariate_normal as MVN

Debug = 0
MEMORYS_WORTH_OF_PARAMETERS = 1e8





def logp_from_resid(x, c, resid_fcn):
	r = resid_fcn(x, c)
	if r is None:
		raise mcmc.NotGoodPosition
	return -numpy.sum(r**2)/2.0



def _print(fd, prefix, p):
	fd.writelines( ' '.join( [prefix] + [ '%g'%pj for pj in p ] ) )
	fd.writelines('\n')


def _read(fd):
	o = []
	for t in fd:
		if t.startswith('#'):
			continue
		t = t.strip()
		if t == '':
			continue
		o.append( numpy.array( [float(x) for x in t.split() ],
					numpy.float)
			)
	np = o[-1].shape[0]
	# die.info("np=%d" % np)
	return o[ max(0, len(o)-2*np*np) : ]




def go(argv, theStepper):
	"""Run the optimization, controlled by command line flags."""
	global Debug
	import load_mod
	if len(argv) <= 1:
		print __doc__
		return
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
		elif arg == '-debug':
			Debug += 1
		elif arg == '--':
			break
		else:
			die.die("Unrecognized flag: %s" % arg)
	
	assert python is not None, "Need to use the -py flag."

	mod = load_mod.load_named_module(python, use_sys_path='/' in python)
	print "# mod= %s" % str(mod)

	if out:
		logfd = open(out, "w")
	else:
		logfd = None

	mod_c = getattr(mod, "c", None)
	if not hasattr(mod, "start"):
		start = _read(sys.stdin)
	else:
		start = mod.start(arglist, mod_c)

	if hasattr(mod, 'logp'):
		logPfcn = mod.logp
	elif hasattr(mod, 'resid'):
		logPfcn = lambda x, c, m=mod: logp_from_resid(x, c, m.resid)
	else:
		die.die("Can't find logp() or resid() function in module.")

	if NI is None:
		NI = mod.NI
	print "# NI= %d" % NI


	mod_c = getattr(mod, "c", None)	#A kluge, in case mod.start() changed c.
	if hasattr(mod, "V"):
		V = numpy.asarray(mod.V(start, mod_c), numpy.float)
	elif mcmc.start_is_list_a(start) and len(start)>1:
		V = mcmc.diag_variance(start)
	else:
		V = numpy.identity(start[0].shape[0], numpy.float)

	mod_c = getattr(mod, "c", None)	#A kluge, in case mod.V() changed c.
	if hasattr(mod, "init"):
		logptr = mod.init(V.shape[0], NI, mod_c, arglist)
	else:
		logptr = def_logger(V.shape[0], NI, mod_c, arglist)

	sort = getattr(mod, 'SORT_STRATEGY', mcmc.BootStepper.SSAUTO)

	fixer = getattr(mod, 'fixer', None)

	mod_c = getattr(mod, "c", None)	#A kluge, in case mod.init() changed c.
	sys.stdout.flush()
	x = theStepper(logPfcn, start, V, c=mod_c, sort=sort, fixer=fixer)

	sys.stdout.writelines('[P]\n')
	for i in range(NI):
		x.step()
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


class def_logger:
	def __init__(self, ndim, ni, c, arglist):
		self.v = numpy.zeros((ndim,ndim), numpy.float)
		self.n = 0
		self.NI = ni
		self.c = c
	
	def add(self, p, i):
		if i >= self.NI/10:
			self.v += numpy.outer(p, p)
			self.n += 1

	def finish(self, stdout):
		self.v /= float(self.n)
		sys.stdout.writelines('[V]\n')
		sys.stderr.writelines(str( self.v ) + "\n")
		evalues, evec = numpy.linalg.eigh(self.v)
		stdout.writelines('[Evals]\n')
		stdout.writelines("%s\n" % str(evalues))
		stdout.writelines('[Evecs]\n')
		stdout.writelines("%s\n" % str(evec))






if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	try:
		go(sys.argv, mcmc.bootstepper)
	except:
		die.catch('Unexpected exception')
		raise
