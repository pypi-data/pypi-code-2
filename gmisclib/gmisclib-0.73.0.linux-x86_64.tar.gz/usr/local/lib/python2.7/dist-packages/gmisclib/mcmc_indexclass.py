"""This module provides several classes to manage the parameters of an algorithm,
particularly so that you can run the mcmc.py optimizer on it.  Essentially, the main
problem that it solves is how to keep track of human-readable names assigned to
components of a vector of parameters.

You have an L{index_base} object C{i}, and out can get a parameter from it
like this:  C{i.p("velocity", "car", "x")}.   That would get out a number that
might correspond to the x-velocity of a car.   That's the human-readable side,
but you can also get a vector of all the parameters via C{i.get_prms()} and
get a mapping between names and indices into that vector via C{i.map}.

You can also have parameters that do not appear in the vector
of adjustable parameters.
These are known as "fixed" parameters; their intent is to let you
fix some of the parameters of an optimization, and let the optimizer
play with the remainder.

Use L{guess} first to establish the mapping, write it to a file
and guess reasonable starting values for an optimization.
Then, use L{index} to get parameter values corresponding to names.
"""

import re
import os

import numpy

import die
import dictops
import g_encode

Debug = False


class IndexKeyError(KeyError):
	def __init__(self, *a):
		KeyError.__init__(self, *a)


class index_base(object):
	_e = g_encode.encoder(notallowed=' %,')

	def __init__(self, keymap, name=None):
		assert isinstance(keymap, dict), "Keymap must be a dict, not %s: %s" % (type(keymap), keymap)
		self.map = keymap
		self._p = {}
		self.name = name
		self.modified = 0

	def clear(self):
		self._p = {}
		self.modified = 0

	def p(self, *key):
		raise RuntimeError, 'Virtual Function'

	def p_lower(self, ll, *key):
		raise RuntimeError, 'Virtual Function'

	def p_range(self, lb, ub, *key):
		raise RuntimeError, 'Virtual Function'


	def pN(self, num, *key):
		return [self.p( *(key+(str(i),)) )
				for i in range(num)
				]


	def pNr(self, num, low, high, *key):
		return [self.p_range(low, high, *(key+(str(i),)) )
				for i in range(num)
				]

	def pNl(self, num, low, high, *key):
		return [self.p_lower(low, high, *(key+(str(i),)) )
				for i in range(num)
				]


	def get_prms(self):
		"""@return: a vector of the adjustable parameters
		@rtype: L{numpy.ndarray}
		"""
		raise RuntimeError, 'Virtual Function'


	def columns(self):
		cols = [None] * len(self.map)
		for (k, i) in self.map.items():
			cols[i] = self._fmt(k)
		return cols


	def n(self):
		"""@return: the number of adjustable parameters.
		@rtype: int
		@note: to include the number of fixed parameters, you can take C{len(self._p)}.
		"""
		return len(self.map)


	@classmethod
	def _unfmt(cls, s):
		"""This converts the in-file format of a parameter name (a comma separated string)
		into the in-memory format (a tuple).
		@param s: parameter name made of parameter-separated components
		@type s: str
		@return tuple-formated parameter name
		@rtype tuple(str)
		"""
		return tuple( [ cls._e.back(q) for q in s.split(',')] )


	@classmethod
	def _fmt(cls, key):
		for kq in key:
			assert isinstance(kq, str), "Key is not entirely composed of strings: %s" % repr(key)
		return ','.join( [ cls._e.fwd(kq) for kq in key]  )


	def i_k_val(self):
		rv = []
		for (k, v) in self.map.items():
			rv.append( (v, k, self.p(*k)) )
		rv.sort()
		return rv


	def comment(self, c):
		pass
	
	
	def hash(self):
		return hash(tuple(sorted(self.map.items())))
	
	def __call__(self):
		raise RuntimeError, "Virtual method - returns a float"

	def logdens(self, x):
		raise RuntimeError, "Virtual method - returns a float"

	def set_all_fixed(self, kv):
		"""This sets a whole dictionary's worth of fixed parameters.
		@param kv: parameters to set
		@type kv: dict
		"""
		self._p.update(kv)
		self.modified += 1

	def set_fixed(self, v, *k):
		"""You can have "fixed" parameters that are not updated by the MCMC optimizer.
		This sets one of them.
		@param v: the value
		@param k: the key.
		"""
		self._p[k] = v
		self.modified += 1
		

	def get_fixed(self):
		"""Get only the fixed parameters.
		@rtype: a dictionary from parameter name to value.
		"""
		rv = {}
		for (k, v) in self._p.items():
			if k not in self.map:
				rv[k] = v
		return rv




class MissingParameterError(KeyError):
	def __init__(self, *s):
		 KeyError.__init__(self, *s)


def _get_doc(fcn):
        try:
                doc = fcn.__doc__
                # doc = getattr(fcn, '__doc__')
        except AttributeError:
                doc = str(fcn)
        return doc


class sampler(object):
        def __init__(self):
                pass

        def __call__(self):
                raise RuntimeError, "Virtual method - returns a float"

        def logdens(self, x):
                raise RuntimeError, "Virtual method - returns a float"




class guess(index_base):
	def __init__(self, guesses, fp=None, name=''):
		"""Create an object that produces the initial guesses at parameter values.
		Feed it a list of patterns that match parameter names, each with a function to
		produce a random guess for that parameter.   When you request the value of
		a parameter via C{self.p} or similar, it will look up the parameter name,
		find the first regular expression that matches it, and call the associated
		function to generate a random value for that parameter.

		@type guesses: list(tuple(str, L{sampler}))
		@param guesses: a list of C{(pattern, sampler)} tuples, where
			C{pattern} is an (uncompiled) regular expression,
			C{sampler} is a function (or class) that produces samples from some
			probability distribution.  C{Sampler} is
			called without arguments, once for each parameter, for each guess that is needed.
			The C{pattern} selects for which parameters C{sampler} will be used.
			It must match the entire parameter name; it will be surrounded by "^$" before
			use.
		@param fp: an open file which can be used as a log, or None.
		@type fp: a writeable C{file} object.
		@param name: a named for the indexer.   It is just stored away, and may be accessed
			as the "name" attribute.
		@type name: anything.
		"""
		index_base.__init__(self, {}, name=name)
		try:
			for (pat,sampler) in guesses:
				assert isinstance(pat, str)
				assert hasattr(sampler, '__call__'), "Must be a callable object (e.g. function)"
		except ValueError, x:
			raise ValueError(*(('Guesses needs to be a 2-tuple', str(x), 'guesses:',)+tuple(guesses)))
		self.guesses = [ (re.compile('^%s$' % pat), sampler) for (pat,sampler) in guesses ]
		self.fp = fp
		if fp is not None:
			fp.writelines('# ------------------------------------\n')
		self.active = True
		self.pmaker = {}
		self.header = {}
		self.user = None
		self._usage = dictops.dict_of_sets()
		if fp is not None and hasattr(fp, 'name'):
			self.header['mapfname'] = fp.name


	def comment(self, c):
		if self.fp is not None:
			self.fp.writelines(['#', str(c), '\n'])
			self.fp.flush()

	def clear(self):
		index_base.clear(self)
		self._usage = dictops.dict_of_sets()

	def get_prms(self):
		"""This L{freeze}s your set of parameters so no more will be added,
		and then returns the current guess for all the adjustable parameters.
		@return: a vector of the adjustable parameters
		@rtype: L{numpy.ndarray}
		"""
		self.freeze()
		a = numpy.zeros((self.n(),))
		for (k,i) in self.map.items():
			try:
				a.itemset(i, self._p[k])
			except KeyError:
				a.itemset(i, self.pmaker[k]() )
		self._p = {}
		return a


	def _wrerr(self, text, key):
		if self.fp is not None:
			fmtd = self._fmt(key)
			self.fp.writelines('ERR: %s %s\n' % (text, fmtd))
			self.fp.flush()


	_fnsp = re.compile('/([^/]*)(?=/)')


	def _write(self, key, extra_stackdrop=0):
		if self.fp is not None:
			import inspect
			import avio
			fmtd = self._fmt(key)
			stack = []
			for (fro, fname, lnum, funcname, context, icontext) in inspect.stack()[2+extra_stackdrop:]:
				del fro
				fname = self._fnsp.sub(lambda g: g.group(0)[:2], fname)
				stack.append( '%s(%s:%d)' % (funcname, fname, lnum) )
			tmp = {'key': fmtd, 'index': self.map[key],
				'stack': ','.join(stack),
				'name': self.name
				}
			self.fp.writelines(avio.concoct(tmp) + '\n')
			self.fp.flush()


	def _compute(self, key, fixer, extra_stackdrop):
		try:
			return self._p[key]
		except KeyError:
			pass
		try:
			self._p[key] = self.pmaker[key]()
		except KeyError:
			if not self.active:
				raise MissingParameterError(key)
		self.map[key] = len(self.pmaker)
		vv = None
		fkey = self._fmt(key)
		for (pat, fcn) in self.guesses:
			if pat.match(fkey):
				vv = fcn
				break
		if vv is None:
			raise KeyError, "No match found for '%s'" % fkey

		if fixer is not None:
			v = lambda: fixer(vv())
			v.__doc__ = '%s(%s)' % (_get_doc(fixer), _get_doc(vv))
		else:
			v = vv
		self.pmaker[key] = v
		tmp = v()
		self._p[key] = tmp
		self._write(key, extra_stackdrop)
		if self.user is not None:
			self._usage.add(self.map[key], self.user)
		return tmp


	def __repr__(self):
		s = []
		for k in self.map.keys():
			s.append('%s=%s=%s' % (','.join(k),
						_get_doc(self.pmaker[k]),
						str(self._p[k])))
		s.sort()
		s.insert(0, "active" if self.active else "frozen")
		return '<guess: %s>' % '\n\t'.join(s)


	def set_user(self, user):
		self.user = user


	def usage(self):
		"""Tells you which users access each index.
		@returns: L{dictops.dict_of_sets} (approximately a dict)
			indexed by integer indices and mapping to a set of users.
			e.g. {3: set(['user1', 'user2']), ...}.
		"""
		return self._usage


	def p(self, *key):
		return self._compute(key, None, 0)

	pc = p

	def p_lower(self, ll, *key):
		"""A range, with a lower limit."""
		def fix_ll(x):
			if x < ll:
				return 2*ll - x
			return x
		fix_ll.__doc__ = "lower limit %g" % ll
		return self._compute(key, fix_ll, 0)

	pc_lower = p_lower


	def p_range(self, lb, ub, *key):
		assert ub > lb, "Bad range: %s<%s for %s" % (str(ub), str(lb), str(key))
		"""A range, folding at the ends."""
		def fix_range(v):
			if not ( lb <= v <= ub):
				r = ub - lb
				tmp = (v-lb) % (2*r)
				v = lb + (tmp if tmp<=r else 2*r-tmp)
			return v
		fix_range.__doc__ = "range from %g to %g" % (lb, ub)
		return self._compute(key, fix_range, 0)


	def p_periodic(self, ub, *key):
		"""A range with periodic boundary conditions 0 to ub."""
		assert ub > 0
		def fix_range(v):
			return v % ub
		fix_range.__doc__ = "periodic from 0 to %g" % ub
		return self._compute(key, fix_range, 0)


	def freeze(self):
		"""This call means that all parameter names have been seen.
		Any novel names in calls to C{self.p()} will then raise an error.
		"""
		self.active = False


	def set_prm(self, v, *key):
		"""This function is used to adjust parameters in non-trivial ways.
		"""
		self.modified += 1
		self._p[key] = v
		if Debug:
			die.info('set_prm on guess: %g %s' % (v, str(key)))






class index(index_base):

	reprkeys = re.compile('.')

	def __init__(self, keymap, p=None, name='', fixed=None):
		assert isinstance(keymap, dict)
		index_base.__init__(self, keymap, name=name)
		assert p is None or len(p) == len(keymap)
		self._prms = None
		self._hashmod = -1
		if p is not None:
			self.set_prms(p)
		if fixed is not None:
			self.set_all_fixed(fixed)
		# self.hash()
	

	def hash(self):
		if self._hashmod == self.modified:
			return self._hashcache
		phash = hash(tuple(self._p.values()))
		self._hashcache = hash( (index_base.hash(self), phash, self.modified) )
		self._hashmod = self.modified
		return self._hashcache


	def clear(self):
		index_base.clear(self)
		self._prms = None
		self._hashmod = -1

	def set_prms(self, prm):
		"""This sets the vector of parameters to be used and modified.
		Note that p_lower() can affect the prm argument! No copy is
		made and this side effect is needed for the problem_definition.fixer()
		function.

		This function should only be called after the map is established.
		"""
		assert prm.shape == (len(self.map),)
		self.modified = 0
		self._hashmod = -1
		self._prms = prm
		for (k, v) in self.map.items():
			self._p[k] = prm[v]


	def set_prm(self, v, *key):
		"""This sets one element of the parameters vector.
		This function should only be called after the map is established; it cannot be used to set fixed parameters.
		"""
		try:
			self._prms.itemset(self.map[key], v)
		except KeyError:
			raise IndexKeyError(key, self)
		self._p[key] = v
		self.modified += 1


	def p(self, *key):
		try:
			return self._p[key]
		except KeyError:
			raise IndexKeyError(key, self)


	def p_lower(self, ll, *key):
		"""@note: this may have side effects on the array passed to prms().
		@except KeyError: when you apply it to a fixed parameter below the specified C{ll}.
		"""
		try:
			v = self._p[key]
		except KeyError:
			raise IndexKeyError(key, self)
		if v < ll:
			v = 2.0*ll - v
			self.modified += 1
			self._prms.itemset(self.map[key], v)
			self._p[key] = v
		return v


	def p_range(self, lb, ub, *key):
		"""@note: this may have side effects on the array passed to prms().
		@except KeyError: when you apply it to a fixed parameter outside specified range C{(lb,ub)}.
		"""
		try:
			v = self._p[key]
		except KeyError:
			raise IndexKeyError(key, self)
		if not (lb <= v <= ub):
			assert ub > lb
			r = ub - lb
			tmp = (v-ub) % (2*r)
			v = lb + (tmp if tmp<=r else 2*r-tmp)
			self.modified += 1
			self._p[key] = v
			self._prms.itemset(self.map[key], v)
		return v


	def p_periodic(self, ub, *key):
		"""A range with periodic boundary conditions 0 to ub.
		@note: this may have side effects on the array passed to prms().
		@except KeyError: when you apply it to a fixed parameter outside specified range C{(lb,ub)}.
		"""
		try:
			v = self._p[key]
		except KeyError:
			raise IndexKeyError(key, self)
		if not (0 <= v < ub):
			assert ub > 0
			v = v % ub
			self.modified += 1
			self._p[key] = v
			self._prms.itemset(self.map[key], v)
		return v

	pc = p
	pc_lower = p_lower
	

	def get_prms(self):
		"""@return: a vector of the adjustable parameters
		@rtype: L{numpy.ndarray}
		"""
		return self._prms


	def toDisplay(self, reprkeys=None):
		"""@note: This prints the values without the folding or wrapping that is done by
			L{p_range}, L{p_periodic}, L{p_lower}, or L{p_upper}.   So, you should not
			be surprised or disturbed if you see a value outside the expected range.
			If you extract the values normally, using the p_* accessor funcitons,
			all will be well.
		"""
		if reprkeys is None:
			reprkeys = self.reprkeys
		tmp = []
		for k in self.map.keys():
			ifk = index._fmt(k)
			if reprkeys.match(ifk):
				tmp.append("%s=%.3f" % (index._fmt(k), self.p(*k)) )
		if len(tmp) < self.n():
			tmp.append('...')
		tmp.sort()
		return ', '.join(tmp)


	def __repr__(self):
		return '<Index:%s %s>' % (self.name, self.toDisplay())


	def items(self):
		"""@return: a sequence of all the parameter, fixed or adjustable.
		@rtype: sequence( (key, value) ) where C{key} could be anything hashable,
			but is usually a tuple of strings, and C{value} is a L{float}.
		"""
		return self._p.items()
	
	def keys(self):
		return self._p.keys()


def default_mapfp(nmprefix='m'):
	import time
	import gpkmisc
	gpkmisc.makedirs('MAPS')
	# os.system('mkdir -p MAPS')
	fname = time.strftime('%Y%m%d-%H%M%S.map')
	fp = open(os.path.join('MAPS', '%s%s' % (nmprefix, fname)),
				'w')
	return fp


def guess_to_indexer(g):
	assert isinstance(g, guess)
	return index(g.map, g.get_prms(), name=g.name, fixed=g.get_fixed())
	
	
def reindex(q, ref):
	"""This remaps the parameters of C{q} so that they are in
	the same order as in C{ref}.
	@rtype: indexer
	@return: an indexer that contains the same data as C{q}, but shares its parameter mapping with C{ref}.
	@note: The parameters in C{q} must be a superset of the adjustable
		parameters in C{ref}.  Extra parameters in C{q} will be
		carried over as fixed parameters.
	"""
	if set(q.keys()) != set(ref.keys()):
		rk = set(ref.keys())
		qk = set(q.keys())
		die.info("Common parameters: %s" % str(rk.intersection(qk)))
		die.info("Parameters only in q: %s" % str(qk-rk))
		die.info("Parameters only in ref: %s" % str(rk-qk))
	rvn = numpy.zeros((ref.n(),))
	rvf = {}
	for (k,i) in ref.map.items():
		rvn[i] = q.p(*k)
	for (k, v) in q.items():
		if k not in ref.map:
			rvf[k] = v
	return index(ref.map, p=rvn, name=q.name, fixed=rvf)




class index_counted(index):
	"""This is a special-purpose wrapped version of L{index}.
	Its only function is to make sure that all parameters were
	used, in addition to the normal checking that you do not use
	any parameters that are undefined.

	Use it exactly as you would use L{index}, but it is slower.
	"""

	def __init__(self, idxr):
		index.__init__(self, idxr.map, idxr.get_prms(), name=idxr.name)
		self.used = set()

	def p(self, *key):
		self.used.add(key)
		return index.p(self, *key)

	def p_lower(self, ll, *key):
		self.used.add(key)
		return index.p_lower(self, ll, *key)

	def p_range(self, lb, ub, *key):
		self.used.add(key)
		return index.p_range(self, lb, ub, *key)

	def p_periodic(self, ub, *key):
		self.used.add(key)
		return index.p_periodic(self, ub, *key)
	
	def confirm_all_used(self):
		"""This can be used to check that we aren't using an indexer with
		a problem that is too small (for instance, if the indexer was read in
		from a log file).
		@except IndexKeyError: if there are some keys in the index that have not
			been used.
		"""
		sm = set(self.map.keys())
		if self.used != sm:
			die.info("used keys: %s" % self.used)
			die.info("keys in map: %s" % self.map.keys())
			raise IndexKeyError("Unused keys:", sm-self.used)
