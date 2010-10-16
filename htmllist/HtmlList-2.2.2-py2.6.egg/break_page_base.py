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
An abstract base class for classes that break the HTML pages, produces a symbols
(Tags) sequence for the RepeatPattern classes, gets back the results, and
generates the HTML sub sections (these are the selected patterns).

As a convention, to the symbols a RepeatPattern classes works with I call Tags,
and these are a tag_tools.Tag instances. To the symbols the sub classes of this
class works with I call Elements. An element object will be different in each
implementation of this base class, and the user should not call any of it's
methods. This class defines a set of class-methods to work with an elements
sequence.

This class has two "public" TagSet objects, "include_tags" if not empty, will
hold the tags to include (and only them), and "exclude_tags" if not empty, will
hold the tags to always exclude from the sequence returned by "get_tag_list".
See TagSet documentation for more details.

This class creates a singleton object.
"""

# NOTE: Python 2.6 Only
from abc import ABCMeta, abstractmethod

from tag_tools import TagSet

class BreakPageBase(object):
	""" Abstract base class for the BreakXXX classes. """

	__metaclass__ = ABCMeta

	# This is the default excluding tags (as strings),
	# I don't think we will ever need to change them.
	DEF_EXCLUDE_TAGS = "html", "head", "title", "script", "style", "body"

	# Singleton from:
	# http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/#c8
	_instance = None

	def __new__(cls, *args, **kwargs):
		if cls != type(cls._instance):
			cls._instance = object.__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self):
		self.include_tags = TagSet()
		self.exclude_tags = TagSet()
		self.exclude_tags += self.DEF_EXCLUDE_TAGS

	@abstractmethod
	def element_by_tag_index(self, index):
		""" Return an element from the orig_lst by a Tag index from the tag_lst.
		I need it for other modules (not for this class or RepeatPattern).
		"""

	@abstractmethod
	def feed(self, data):
		""" Add text to be parsed. """

	@abstractmethod
	def close(self):
		""" Should be called after all HTML text has been feed in. """

	@abstractmethod
	def clear(self):
		""" Clear all old data """

	@abstractmethod
	def get_tag_list(self):
		""" Return an iterator of tags in the HTML body. Each tag is a Tag
		instance.
		"""

	@abstractmethod
	def get_text_list(self, lst):
		""" Return an iterator over lists of elements in an HTML page.
		These lists are the sections we may be interested in.
		The iterator item is a two-tuple (list, next). next is the first element
		in the next list (or None). It is used to stop the rendering of the HTML
		section (to avoid overlapping)

		list is a two-tuple list of (start, end) indices in the sequence
		"get_tag_list" returned. These are the occurrences of the selected
		pattern.
		"""

	## Class Methods ##

	@classmethod
	@abstractmethod
	def traverse_list(cls, elm_lst, elm_func, elm_close_func=None, stop_elm=None):
		""" Traverse the elements list until the end or until it gets to
		'stop_elm'. On every element it applies 'elm_func', if the result is not
		None the method returns it. On every close element it applies
		'elm_close_func' if it is not None, if the result is not None the
		method returns it.

		This is the only access to every element in an HTML section!
		"""

	@classmethod
	@abstractmethod
	def list2text(cls, lst, stop_elm=None):
		""" Render the HTML text a list of HTML elements represent.
		It takes an optional second argument, stop_elm, which will stop the
		rendering of the HTML if it finds this tag in one of the child tags, so
		the returned HTML sections will not overlap, even if one of the tags in
		the list spans over the next list (which will start with the stop_elm).
		"""

	@classmethod
	def validate_list(cls, elm_lst, stop_elm=None, good_elm_func=None):
		""" Scans the sub HTML Elements that in the elm_lst range, until it
		finds an element that good_elm_func returns True on it. This is
		basically only a wrapper on traverse_list, and I can give default
		implementation here.

		elm_lst - A list of the implementing class elements.
		stop_elm An optional element to stop the scan on (like in list2text).
		good_elm_func An optional function that take Element and return boolean
		or None. The default function checks if the element contains some text.

		Returns True if found an element such as the above, or False.
		"""
		if not good_elm_func:
			good_elm_func = cls.is_text_elm
		return bool(cls.traverse_list(elm_lst, good_elm_func, stop_elm=stop_elm))

	## Class Method to work with Elements ##

	@classmethod
	@abstractmethod
	def words_between_elements(cls, start, end):
		""" Count the number of words in an HTML section """

	@classmethod
	@abstractmethod
	def get_element_name(cls, elm):
		""" Return the element name """

	@classmethod
	@abstractmethod
	def get_element_attrs(cls, elm):
		""" Return the element attributes mapping or None if there are no
		attributes to this element.
		"""

	@classmethod
	@abstractmethod
	def get_all_element_data(cls, elm):
		""" A convenience method to get a tuple of all the element data required
		for a Tag creation. The first item in the tuple has to be the tag name,
		the rest is up to the implementing class.
		"""

	@classmethod
	@abstractmethod
	def is_tag_element(cls, elm):
		""" Return True if the element represent a normal (opening) tag in an
		HTML page.
		"""

	@classmethod
	@abstractmethod
	def is_text_elm(cls, elm):
		""" Returns True if an element has some content in it.
		If not it returns None!
		"""

