"""This module provides a way of safely specifing accent
positions in running text.

If you have a transcription "I did not eat the orange ball.",
you can attach a "+" symbol to the word "eat" like this:
"+eat".

You enter an accent specification, which consists of words with
a prefix (the prefix is anything that ends in a punctuation mark).
The program matches up the words in the accent specification
to the words in the transcription.
You can have many words in the accent specification, if necessary.
You can also disambiguate things by putting context words into
the accent spec (without a prefix).
All matching is done left-to-right.
"""

import re

__version__ = "$Revision: 1.4 $"

_goodprefix = re.compile("""^.*\W$""")
_goodsuffix = re.compile("""^\W.*$""")

class BadMatchError(RuntimeError):
	def __init__(self, x):
		RuntimeError.__init__(self, x)

def prefix(text_array, accent_spec, map_fcn=lambda x:x):
	"""This function takes an array of words and an accent spec.
	It matches the accent spec to the words,
	and outputs an array of tuples which tells you
	where the accents are, and what kind.
	The optional map_fcn can be used to map other kinds
	of objects into a array of strings.

	More specifically, an accent_spec is a whitespace-separated
	list of strings.   Each string is a word from the text_array,
	with an optional prefix.   The strings are matched in
	order to the words, and the output array is a list
	of (index_in_text_array, prefix_text) tuples.

	So, if you have text_array = ['my', 'cat', 'is', 'my', 'cat']
	and accent_spec="is +my", then align() will match
	"is" to text_array[2], and "+my" to text_array[3],
	and it will return [ (3, "+") ] .
	Note that "+is +my" does not imply that 'is' and 'my'
	are adjacent, and "+is +cat" simply returns [ (2, "+"), (4, "+") ].

	If the accent_spec were "+my", then it would match
	text_array[0], and return [ (0, "+") ].

	Prefixes can be multiple characters,
	but they cannot end in letters, digits, or underscore.
	"""


	asa = accent_spec.split()
	if len(asa) > len(text_array):
		raise BadMatchError, "Accent spec longer than text array: %d vs. %d" % (len(asa), len(text_array))
	as0 = asa.pop(0)
	out = []
	j = 0
	for t in map_fcn(text_array):
		# print "AS=", as0, "t=", t
		if as0 == t:	# A match for alignment purposes.
			# print "Align match"
			if len(asa) == 0:
				return out
			else:
				as0 = asa.pop(0)
		elif as0.endswith(t) and _goodprefix.match(as0[:-len(t)]):
				# A match with an accent.
			# print "Acc match:", as0[:-len(t)]
			out.append( (j, as0[:-len(t)]) )
			if len(asa) == 0:
				return out
			else:
				as0 = asa.pop(0)
		j += 1
	raise BadMatchError, "Accent_spec not consistent with text:  %d/%d." % (len(asa), len(text_array))




def suffix(text_array, accent_spec, map_fcn=lambda x:x):
	"""See prefix, but with the obvious changes."""

	asa = accent_spec.split()
	if len(asa) > len(text_array):
		raise BadMatchError, "Accent spec longer than text array: %d vs. %d" % (len(asa), len(text_array))
	as0 = asa.pop(0)
	out = []
	j = 0
	for t in map_fcn(text_array):
		# print "AS=", as0, "t=", t
		if as0 == t:	# A match for alignment purposes.
			# print "Align match"
			if len(asa) == 0:
				return out
			else:
				as0 = asa.pop(0)
		elif as0.startswith(t) and _goodsuffix.match(as0[len(t):]):
				# A match with an accent.
			# print "Acc match:", as0[:-len(t)]
			out.append( (j, as0[len(t):]) )
			if len(asa) == 0:
				return out
			else:
				as0 = asa.pop(0)
		j += 1
	raise BadMatchError, "Accent_spec not consistent with text:  %d/%d." % (len(asa), len(text_array))



def preshow(text_array, alignment, map_fcn=lambda x:x):
	"""Shows an alignment in a printable form.
	It puts the prefixes in the appropriate places.
	"""
	tm = [ map_fcn(t) for t in text_array ]
	for (idx, tag) in alignment:
		tm[idx] = tag + tm[idx]
	return tm



def sufshow(text_array, alignment, map_fcn=lambda x:x):
	"""Shows an alignment in a printable form.
	It puts the suffixes in the appropriate places.
	"""
	tm = [ map_fcn(t) for t in text_array ]
	for (idx, tag) in alignment:
		tm[idx] = tm[idx] + tag
	return tm




def test():
	ta = ['my', 'cat', 'is', 'my', 'cat']
	assert prefix(ta, "is +my") == [ (3, '+') ]
	assert prefix(ta, "+my") == [ (0, '+') ]
	assert suffix(ta, "my+") == [ (0, '+') ]
	assert preshow(['my', 'cat', 'Fred'], [(1, '!')]) == ['my', '!cat', 'Fred']
	assert sufshow(['my', 'cat'], [(1, '!')]) == ['my', 'cat!']


if __name__ == '__main__':
	test()
	import sys
	arglist = sys.argv[1:]
	pre = 1
	if len(arglist)>0 and arglist[0] == '-s':
		pre = 0
		arglist.pop(0)
	elif len(arglist)>0 and arglist[0] == '-p':
		pre = 1
		arglist.pop(0)
	textarray = arglist
	accspec = sys.stdin.readline().strip()
	if pre:
		alignment = prefix(textarray, accspec)
		print ' '.join(preshow(textarray, alignment))
	else:
		alignment = suffix(textarray, accspec)
		print ' '.join(sufshow(textarray, alignment))
