#!python

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
This module define HtmlListBreak which makes sure every HTML section has some
text in it. It is also calculating the average number of words that in the HTML
list. The counting is done BEFORE rendering the list text.
"""

from htmllist_base import HtmlList, InvalidListException

class HtmlListBreak(HtmlList):
	""" """
	def handle_sub_html(self, lst, next):
		""" Add validation that a sub HTML section has some text in it. """
		# If I throw InvalidListException from this method, the list will
		# bee discarded
		if not self._bhp.validate_list(lst, next):
			raise InvalidListException()
		return HtmlList.handle_sub_html(self, lst, next)

	def _find_last_element(self, elm):
		""" keep reference to the last element """
		if not elm in self._elm_set:
			self._elm_set.add(elm)
			self.last_elm = elm


	def avrg_words_in_section(self):
		""" Return the approximate average number of words in a sub HTML section.
		I use a method that returns None as an argument to the traverse_list
		function, to find the last element of the section.
		"""
		self._elm_set = set() # Keep track of visited elements
		html_lst = self.break_cls.get_text_list(self.pattern_cls.indices_lst)
		total = count = 0
		for lst, next in html_lst:
			count += 1
			self.break_cls.traverse_list(lst, self._find_last_element,
				self._find_last_element, stop_elm=next)
			total += self.break_cls.words_between_elements(lst[0], self.last_elm)
		if count == 0: return 0
		return float(total) / count

if __name__ == '__main__':
	pass
	# TODO: Add a unit test

