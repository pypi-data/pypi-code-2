# HtmlList - Finds repetitive format patterns in an HTML page.
# Copyright (C) 2010  Erez Bibi (erezbibi@users.sourceforge.net)
#
# This file is part of HtmlList.
#
# HtmlList is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HtmlList is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HtmlList.  If not, see <http://www.gnu.org/licenses/>.

"""
This module defines a few classes that simplify the dealing with HTML tags.
BreakHtmlPage uses them, and it is decoupled from the 3rd party tool that
BreakHtmlPage use to parse the HTML text.
"""

# This is not likely to change, and there is not an easy interface to change it.
FORMAT_ATTRIBUTES = "class", "style", "type", "headers" #, "width"

class Tag(object):
	"""
	Represent a simple HTML tag with optional formating attributes.
	I calculate the hash value in advance, for efficiency.
	I need this class to easily compare tags with each other.
	These are the "items" RepeatPattern uses.

	other_info can be any arbitrary additional information about the tag. It
	has to be "hashable".
	"""
	__slots__ = "_name", "_attrs", "_hash", "_info"

	def __init__(self, name, attrs=None, other_info=None):
		self._name = name.lower()
		self._info = other_info
		if attrs:
			self._attrs = tuple((name, val) for name, val in attrs.items() \
				if name in FORMAT_ATTRIBUTES)
		else:
			self._attrs = None
		self._hash = hash((self._name, self._attrs, self._info))

	def __repr__(self):
		""" Print for debugging """
		if self._attrs:
			attrs = ' ' + ','.join('%s="%s"' % (name, val) for \
				name, val in self._attrs
			)
		else: attrs = ''
		if self._info:
			info = " (%s)" % self._info
		else: info = ''
		return "<%s%s%s>" % (self._name, attrs, info)

	def __hash__(self):
		return self._hash

	def __cmp__(self, other):
		if other is None: return 1
		# Surprisingly this is about twice as fast
		return (self._hash > other._hash) - (self._hash < other._hash)
		#return cmp(self._hash, other._hash)

	def tag_name(self):
		""" Return the tag name. I need it for the TagSet class. """
		return self._name

	def tag_attrs(self):
		""" Return the tag attributes (two-tuple) list, or None """
		return self._attrs

	def get_info(self):
		""" Return the tag "other" information if exists or None """
		return self._info


class TagSet(object):
	""" This class holds two sets, one of Tags, and one of strings.
	The class implement the __contains__ operator. The item to test is always a
	Tag, it checks the tags set first, if it is not there, it checks if the Tag
	name is in the strings set.

	The class also have a += operator. It adds elements to both sets like
	'update'. One can add a Tags or a string or tuples/lists/sets of Tags and
	strings.
	"""
	def __init__(self):
		""" """
		self._set_tags = set()
		self._set_strs = set()

	def __iadd__(self, other):
		""" Add Tags or strings or sequence of Tags and strings """
		if not other: return self
		if type(other).__name__ not in ("set", "list", "tuple", "generator"):
			other = [other]
		tags = []
		strs = []
		for item in other:
			if isinstance(item, Tag):
				tags.append(item)
			else:
				strs.append(str(item))
		self._set_tags.update(tags)
		self._set_strs.update(strs)
		return self

	def __contains__(self, item):
		""" Check if an item is in one of the sets. 'item' will always be a Tag
		object. Checks first if an identical Tag object is in the tags set. If
		not, checks if the Tag name is in the strings set.
		"""
		assert isinstance(item, Tag), "'item' has to be a Tag"
		return item in self._set_tags or item.tag_name() in self._set_strs

	def __len__(self):
		""" The length of both sets """
		return len(self._set_tags) + len(self._set_strs)

	def __nonzero__(self):
		""" At least one of the sets is not empty """
		return bool(self._set_strs) or bool(self._set_tags)

	def __repr__(self):
		""" For debugging mainly """
		return "Tags: %s\nStrings: %s" % (self._set_tags, self._set_strs)

	def clear(self):
		""" Clear both sets """
		self._set_tags.clear()
		self._set_strs.clear()

	@classmethod
	def test(cls, verbose=False):
		""" Testing of both classes """
		ts = cls()

		ts += "aaa"
		ts += "aaa", "bbb"
		ts += ["aaa", "bbb", "ccc"]
		ts += set(("ccc", "ddd"))
		ts += Tag("aaa")
		ts += Tag("eee"), Tag("fff", {"class": "foo"})

		if verbose:
			print ts

		assert Tag("aaa") in ts
		assert Tag("ccc", {"type": "foo"}) in ts
		assert Tag("eee") in ts
		assert Tag("eee", {"class": "bar"}) not in ts
		assert Tag("fff", {"class": "foo"}) in ts
		assert Tag("fff", {"class": "bar"}) not in ts

## A list of HTML container tags (or tags it is good to start a pattern with) ##
CONTAINER_TAGS = TagSet()
CONTAINER_TAGS += "div", "span", "li", "tr", "h2", "h3", "h4"


if __name__ == '__main__':
	TagSet.test(verbose=True)
	print "Test Passed"

