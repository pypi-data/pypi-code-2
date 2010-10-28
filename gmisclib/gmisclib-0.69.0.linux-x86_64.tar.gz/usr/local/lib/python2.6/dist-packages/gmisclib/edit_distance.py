
"""Levenshtein (edit) distance between two strings of symbols.
"""

import numpy

def dist(s, t, csub, cinsert, cdel):
	"""Cost for converting string s into string t.   This function
	takes three dictionaries that contain the cost of insertion, deletion,
	and substitutions.

	@param s: starting string
	@param t: ending string
	@type s: string or array
	@type t: string or array
	@param csub: cost of converting a to b
	@type csub: dict((a,b) : float)
	@param cinsert: cost of insertion
	@type cinsert: dict(a: float)
	@param cdel: cost of deletion
	@type cdel: dict(a: float)
	"""
	def f(a, b):
		if a is None:
			return cinsert[b]
		elif b is None:
			return cdel[a]
		return csub[(a, b)]
	return distf(s, t, f)


def distf1(s, t, csub):
	"""Cost for converting string C{s} into string C{t}.  This function takes
	a function that computes the cost of insertions, deletions, or substitutions.
	(This is an alternative implementation for C{distf2()}.)

	@param s: starting string
	@param t: ending string
	@type s: string or array
	@type t: string or array
	@param csub: cost of converting a to b
	@type csub: function(a,b) : float
	"""
	m = len(s)
	n = len(t)
	d = numpy.zeros((m+1, n+1), numpy.float)
	for i in range(1, m+1):
		d[i,0] = d[i-1,0] + csub(s[i-1], None)
	for j in range(1, n+1):
		d[0,j] = d[0,j-1] + csub(None, t[j-1])
	
	for j in range(1, n+1):
		for i in range(1, m+1):
			d[i,j] = min(d[i-1,j] + csub(s[i-1], None),  # insertion
					d[i,j-1] + csub(None, t[j-1]),	# deletion
					d[i-1, j-1] + csub(s[i-1], t[j-1])	# sub
					)
	return d[m, n]


def distf2(s, t, csub):
	"""Cost for converting string s into string t.  This function takes
	a function that computes the cost of insertions, deletions, or substitutions.

	@param s: starting string
	@param t: ending string
	@type s: string or array
	@type t: string or array
	@param csub: cost of converting a to b
	@type csub: function(a,b) : float
	"""
	m = len(s)
	n = len(t)
	dj = numpy.zeros((m+1,))
	djm1 = numpy.zeros((m+1,))
	for i in range(1, m+1):
		dj[i] = dj[i-1] + csub(s[i-1], None)
	
	for j in range(1, n+1):
		tmp = djm1
		djm1 = dj
		dj = tmp
		dj[:] = 0.0
		dj[0] = djm1[0] + csub(None, t[j-1])
		for i in range(1, m+1):
			dj[i] = min(dj[i-1] + csub(s[i-1], None),  # insertion
					djm1[i] + csub(None, t[j-1]),	# deletion
					djm1[i-1] + csub(s[i-1], t[j-1])	# sub
					)
	return dj[m]


distf = distf2


def def_cost(a, b):
	"""This is the default cost function for converting C{a} into C{b}.
	Insertions, deletions, and substitutions all have a unit cost.   Normally,
	this is passed as an arg to L{distf}.
	@param a: a symbol (or None to indicate an insertion).
	@param b: a symbol (or None to indicate an deletion).
	@return: the cost of changing C{a} into C{b}
	@rtype: int
	"""
	if a is None or b is None:
		return 1
	if a==b:
		return 0
	return 1


def free_sub(a, b):
	"""This is a sample cost function for converting C{a} into C{b}.
	Insertions and deletions have a unit cost; substitutions are free.   Normally,
	this is passed as an arg to L{distf}.
	@param a: a symbol (or None to indicate an insertion).
	@param b: a symbol (or None to indicate an deletion).
	@return: the cost of changing C{a} into C{b}
	@rtype: int
	"""
	if a is None or b is None:
		return 1
	return 0
	

def free_del(a, b):
	"""This is a sample cost function for converting C{a} into C{b}.
	Insertions and substitutions have a unit cost; deletion are free.   Normally,
	this is passed as an arg to L{distf}.
	@param a: a symbol (or None to indicate an insertion).
	@param b: a symbol (or None to indicate an deletion).
	@return: the cost of changing C{a} into C{b}
	@rtype: int
	"""
	if b is None:
		return 0
	if a is None:
		return 1
	if a==b:
		return 0
	return 1


class text_cost(object):
	"""This is useful for differencing documents that have been parsed
	into lists of words.  It computes the cost of a change of words
	by an edit distance computation on the characters within the words.
	(It caches the costs of commonly encountered words for speed.)
	Instances of this class can be passed as a cost function to
	L{distf}.
	"""

	def __init__(self, costfac=None, cachesize=None, word_cost=None, frac_exp=0.0):
		"""Create an instance.
		@param costfac: None, or an arbitrary function that multiplies the scaled
			edit distance between the two words.   Called as C{self.costfac(a,b)}
			where either C{a} or C{b} can be None for insertions or deletions.
		@type costfac: C{function(str,str): float} or C{None}
		@param cachesize: how large a cache of word-to-word distances should be kept?
		@type cachesize: None (meaning unlimited) or int
		@param word_cost: cost function to use inside words: this is a cost for insertion,
			deletion, or substitution of letters.
		@type word_cost: C{function(str,str): float} or None (meaning use L{def_cost}).
		@param frac_exp: An exponent for scaling the edit distance by the length of words.
		@type frac_exp: float
		"""
		self.costfac = costfac
		self.cache = {}
		assert cachesize is None or cachesize >= 0
		self.cachesize = cachesize

		if word_cost is None:
			self.word_cost = def_cost
		else:
			self.word_cost = word_cost
		self.frac_exp = float(frac_exp)



	def __call__(self, a, b):
		"""To be used by L{distf}.
		@type a: str or None
		@type b: str or None
		@return: a cost
		@rtype: presumably a float
		"""
		if a is None:
			a = ''
		else:
			if a == b:
				return 0.0
		if b is None:
			b = ''

		try:
			return self.cache[(a,b)]
		except KeyError:
			pass

		cost = distf(a, b, self.word_cost)
		cost /= float(max(len(a), len(b)))**self.frac_exp
		if self.cachesize is not None and len(self.cache) > self.cachesize:
			self.cache.pop()
		if self.costfac is not None:
			cost *= self.costfac(a, b)
		self.cache[(a,b)] = cost
		return cost



def test():
	assert distf("hello", "helpo", def_cost) == 1
	assert distf("hello", "helo", def_cost) == 1
	assert distf("hello", "hellox", def_cost) == 1
	assert distf("hello", "helloxx", def_cost) == 2
	assert distf("hello", "elo", def_cost) == 2
	assert distf("hello", "eelpo", def_cost) == 2
	assert distf("kitten", "sitting", def_cost) == 3
	assert distf("saturday", "sunday", def_cost) == 3
	assert distf("hello", "xxxxo", free_sub) == 0
	assert distf("hello", "xxxo", free_sub) == 1
	assert distf("hello", "xxo", free_sub) == 2
	assert distf("hello", "yxxxxo", free_sub) == 1
	assert distf("hello", "yxxxxoy", free_sub) == 2
	assert distf("hello", "hello", free_del) == 0
	assert distf("hello", "helo", free_del) == 0
	assert distf("hello", "hlo", free_del) == 0
	assert distf("helo", "hello", free_del) == 1
	assert distf("hlo", "hello", free_del) == 2
	assert distf("hello", "hallo", free_del) == 1
	assert distf("hlo", "hellp", free_del) == 3


def test2():
	a = ['Now', ' ', 'is', ' ', 'the', ' ', 'time', ' ', 'for', '\n', 'testing', '.']
	b = list(a)
	b[-1] = '!'
	assert distf(a, b, text_cost()) == 1
	b[-3] = '  '
	assert distf(a, b, text_cost()) == 3
	b = list(a)
	b[-4] = 'from'
	assert distf(a, b, text_cost()) == 2
	b[-4:-3] = []
	assert distf(a, b, text_cost()) == 3
	b = list(a)
	b[-4] = 'fir'
	assert abs( distf(a, b, text_cost(frac_exp=1.0)) - 1./3.) < 0.001


if __name__ == '__main__':
	test()
	test2()
