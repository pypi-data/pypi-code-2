# HtmlList - Finds repetitive format patterns in an HTML page.
# Copyright (C) 2010  Erez Bibi (erezbibi@users.sourceforge.net)
#
# This file is part of HtmlList.
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
This module defines the "main" class of HtmlList. It breaks an HTML page that
has some kind of repetitive pattern(s) in it, to the pattern(s) occurrences. It
has one method you use and one method you can overwrite. It uses a RepeatPattern
instance for the pattern recognition algorithm and a BreakHtmlPage instance for
breaking the HTML to a list of elements.

This class wrap the "pubilc" input and "public" output attributes of
RepeatPattern and BreakHtmlPage.
The class is an iterator which is a wrapper for the RepeatPattern class
iterator.

Usae:
	>>> from htmllist.htmllist_base import HtmlList
	>>> hl = HtmlList()
	>>> hl.set_text(some_html_page_taxt)
	>>> hl.process()
	>>> lst = hl.get_html_list()
	>>> if lst:
	...    for itm in lst:
	...        print itm
	... else:
	...    print "Cannot parse the page"

Iterating through this class:
	>>> for i in hl:
	... 	print "Pattern", i, ":", hl.pattern
Will iterate through the patterns (and results) it found on the page.

For comprehensive usage example see htmllist_demo.py
"""

# NOTE: Python 2.6 Only
from collections import Iterable

# All other imports will be from this module
from break_html_page2 import BreakHtmlPage
from break_page_base import BreakPageBase
from repeat_pattern import RepeatPattern # The default algorithm
from utills import not_empty_iter, iter2tuple

class InvalidListException(Exception):
	""" Exception to signal invalid list detection by handle_sub_html """
	pass

class HtmlList(Iterable):
	""" See module documentation """
	def __init__(self, pattern_cls=None, break_cls=None):
		""" Optional Arguments:
		pattern_cls A RepeatPattern class. The default is the class from the
			repeat_pattern model, which implements the new algorithm.
		break_cls A BreakHtmlPage class. The default is the class from the
			break_html_page2 module.
			* IF break_cls is a BreakHtmlPage instance, then HtmlList will use
			it (w/o creating a new object). This is useful when the page is
			already "broken".
		"""
		if not pattern_cls:
			pattern_cls = RepeatPattern
		if not break_cls:
			break_cls = BreakHtmlPage

		self._rp = pattern_cls()
		if isinstance(break_cls, BreakPageBase):
			self._bhp = break_cls
		else:
			self._bhp = break_cls()
		# A flag for valid/invalid result list
		self._is_list_valid = False

	def __setattr__(self, name, value):
		""" Wrapper for RepeatPattern/BreakHtmlPage input attributes """
		if name in ("min_len", "max_len", "min_repeat", "max_repeat",
			"max_stdv", "min_weight", "min_coverage", "min_comp",
			"max_patterns", "debug_level", "pattern_num"):
			setattr(self._rp, name, value)
		elif name in ("element_good", ):
			setattr(self._bhp, name, value)
		else:
			self.__dict__[name] = value

	def __getattr__(self, name):
		""" Wrapper for RepeatPattern/BreakHtmlPage output attributes """
		if name in ("factor", "pattern", "indices_lst", "repeats",
			"relevant_items"):
			return getattr(self._rp, name)
		elif name in ("exclude_tags", "include_tags"):
			return getattr(self._bhp, name)
		else:
			raise AttributeError("HtmlList has not attribute", name)

	def __iter__(self):
		""" Wrapper for RepeatPattern iterator (also set validation flag) """
		for i in self._rp:
			self._is_list_valid = True
			yield i

	@property
	def break_cls(self):
		""" The inner BreakHtmlPage instance,
		so we can pass it to a new HtmlListXXX class if we want to use a different
		algorithm on the same text.
		"""
		return self._bhp

	@property
	def pattern_cls(self):
		""" The inner RepeatPattern instance """
		return self._rp

	@property
	def is_list_valid(self):
		""" Return True if the result HTML list is considered valid.
		The user should always check this value before handling the returned
		HTML list.
		"""
		return self._is_list_valid

	def set_text(self, text):
		""" Break the HTML text and stores it in the BreakHtmlPage object. """
		self._bhp.clear()
		self._bhp.feed(text)
		self._bhp.close()

	def process(self):
		""" Process the HTML page and returns the number of lists found """
		tags = tuple(self._bhp.get_tag_list())
		if not tags: return 0
		return self._rp.process(tags)

	def process_by_pattern(self):
		""" Process the HTML page with a pattern we already found """
		tags = tuple(self._bhp.get_tag_list())
		if not tags: return 0
		return self._rp.process_by_pattern(tags)

	def get_html_sections(self):
		""" Return an iterator of items from handle_sub_html.
		This method breaks the HTML text that was feed with set_text, to sub
		sections we found with the "process" method, according to the inner
		structure of the page. Then it pass each HTML section to handle_sub_html
		and yield the result if it is not None. If handle_sub_html raise
		InvalidListException it sets the list_valid flag to False and stops the
		iteration.
		"""
		html_lst = self._bhp.get_text_list(self._rp.indices_lst)
		self._is_list_valid = True
		for lst, next in html_lst:
			try:
				section = self.handle_sub_html(lst, next)
				if not section is None:
					yield section
			except InvalidListException:
				self._is_list_valid = False
				return

	## get_html_sections that returns not empty iterator or None ##
	get_html_itr = not_empty_iter(get_html_sections)
	## get_html_sections that returns a tuple ##
	# Only with it you can use the list_valid flag
	get_html_list = iter2tuple(get_html_sections)

	def handle_sub_html(self, lst, next):
		""" This method renders the sub HTML of each section.
		You can extend it or overwrite it.

		lst is a list of Tags (from the tag_tools module).
		next is the first tag in the next section (or None)

		It can return None for the section to be ignored.

		When working with get_html_list (only), if this (sub) method raises
		InvalidListException, is_list_valid will get a False value, and the
		result list should be discarded.
		"""
		return self._bhp.list2text(lst, next)

