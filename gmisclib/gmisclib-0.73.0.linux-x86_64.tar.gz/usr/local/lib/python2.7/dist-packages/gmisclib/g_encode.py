# -*- coding: utf-8 -*-
"""This module allows strings to be encoded into a
reduced subset.   It is designed to work for avio.py,
and to do a minimal mapping, so that the resulting
text is human-readable.   It is similar to Quoted-printable
encoding, but is not specialized to e-mail limitations and
is rather more flexible.
"""


import re
import string;


__version__ = "$Revision: 1.10 $"


class BadFormatError(Exception):
	def __init__(self, *x):
		Exception.__init__(self, *x)


_backdict = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5,
		'6':6, '7':7, '8':8, '9':9,
		'a':10, 'A':10, 'b':11, 'B':11,
		'c':12, 'C':12, 'd':13, 'D':13,
		'e':14, 'E':14, 'f':15, 'F':15 }


_specials = [ ('mt', ''),
		(' ', '_'),
		('u', '_'),
		('p', '.'),
		('m', ','),
		('s', ';'),
		('z', '='),
		('t', '\t'),
		('Z', '\033'),
		('M', '&'),
		('T', '%'),
		('l', '/'),
		('K', '\\'),
		('k', '\b'),
		('R', '\r'),
		('L', '\n'),
		('q', '"'),
		('Q', '?'),
		('U', "'"),
		('S', ' '),
		('P', '#')
		]




def _expand_bdict(b):
	o = {}
	for (si, ni) in b.items():
		for (sj, nj) in b.items():
			o[si + sj] = chr(16*ni + nj)
	for (k, v) in _specials:
		assert not _backdict.has_key(k), "Special (%s) collides with hex." % k
		assert not o.has_key(k), "Special (%s) collides with hex or special." % k
		o[k] = v
	return o


_bdict = _expand_bdict(_backdict)


def _fromhex(x):
	"""Expands a %XX code (or the specials above) into a character."""
	q = x.group(1)
	return _bdict[q]



def _rm_nl(s):
	if s.endswith('\n'):
		return s[:-1]
	return s



def _expand_fdict(eschar):
	o = {}
	for c in range(256):
		o[chr(c)] = '%s%02x' % (eschar, c)
	for (k,v) in _specials:
		o[v] = '%s%s' % (eschar, k)
	return o






class encoder:
	def __init__(self, allowed=None, notallowed=None, regex=None, eschar='%'):
		"""
		Note that there are some twiddly points in defining
		encoders -- the notallowed and allowed arguments
		need to be thought through carefully, as they are
		passed into the re module as part of a regular
		expression.    Certain characters may give surprising
		results.
		"""
		assert (regex is not None) + (allowed is not None) + (notallowed is not None) <= 1, "Specify at most one of regex, allowed, notallowed."
		if notallowed is not None:
			assert eschar in notallowed, "Sorry: notallowed must contain '%s', but it is '%s'." % (eschar, notallowed)
			self.ref = re.compile('(^\s)|([%s])|(\s$)' % notallowed)
		elif regex is not None:
			self.ref = re.compile(regex)
		else:
			if allowed is None:
				allowed = string.letters + string.digits + \
						r"""_!@$^&*()+={}[\]\|:'"?/>.<,\ ~`-"""
			assert not eschar in allowed, "Cannot allow '%s'." % eschar
			self.ref = re.compile('(^\s)|([^%s])|(\s$)' % allowed)

		self._reb = re.compile('%s([0-9a-fA-F][0-9a-fA-F]|' % eschar
				+ '|'.join([_c[0] for _c in _specials])
				+ ')')
		self._fdict = _expand_fdict(eschar)
		self.empty = '%smt' % eschar

	def back(self, x):
		"""Converts back from a string containing %xx escape sequences to
		an unencoded string.
		"""
		try:
			return self._reb.sub(_fromhex, x)
		except KeyError, x:
			raise BadFormatError, "illegal escape sequence: %s" % x


	def _tohex(self, x):
		"""Converts a single character in a MatchObject to a %xx escape sequence"""
		q = x.string[x.start()]
		assert len(q)==1, 'tohex operates on a single character'
		return self._fdict[q]


	def fwd(self, x):
		"""Escapes a string so it is suitable for a=v; form.
		Nonprinting characters, along with [;#] are converted
		to %xx escapes (hexadecimal).
		Non-strings will be converted to strings with repr(),
		and can be fed back into the python interpreter.  """
		if not isinstance(x, str):
			x = repr(x)
		if x == '':
			return self.empty
		# print "x=(%s)" % x
		return self.ref.sub(self._tohex, x)




def test():
	e = encoder()
	assert e.back(e.fwd('george')) == 'george'
	assert e.back(e.fwd('hello there')) == 'hello there'
	assert e.back('%sfoo') == ';foo'
	assert e.back('%Sfoo%S%P') == ' foo #'
	assert e.back('%Tfoo') == '%foo'
	assert e.back(e.fwd('%hello')) == '%hello'
	assert e.back(e.fwd(' hello there')) == ' hello there'
	assert e.back(e.fwd(' hello there\t')) == ' hello there\t'
	assert e.back(e.fwd(' hello there\t=')) == ' hello there\t='
	assert e.back(e.fwd(' hello there\t=;#')) == ' hello there\t=;#'
	assert e.back(e.fwd(' hello+_there\t=;#')) == ' hello+_there\t=;#'
	assert e.back(e.fwd('hello+_there\t=;#')) == 'hello+_there\t=;#'
	assert e.fwd('hello there') == 'hello there'

	ee = encoder('abcd')
	assert ee.fwd("cab d") == 'cab%Sd'
	assert ee.fwd("e") == '%65'
	assert ee.fwd("aaaa bbbb") == 'aaaa%Sbbbb'

	ee = encoder(notallowed = ']\n\r%')
	assert '\n' not in ee.fwd('hello world\n\r')
	assert ']' not in ee.fwd('hello]% world\n\r')
	assert ee.back(ee.fwd('hello world\n\r'))=='hello world\n\r'

	e = encoder(eschar='_', allowed='0-9a-zA-Z')
	assert e.back('_sfoo') == ';foo'
	assert e.back(e.fwd('%hello')) == '%hello'
	assert e.back(e.fwd('_hello')) == '_hello'


if __name__ == '__main__' :
	test()
	print "OK: passed tests"
