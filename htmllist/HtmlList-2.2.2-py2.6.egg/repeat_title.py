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
A trivial algorithm to find HTML titles. Some time that is what we need.
I inherit from the module repeat_pattern and not from the base, because there
are common methods here.
"""

from collections import defaultdict

from repeat_pattern import RepeatPattern as RepeatPatternBase

# Multiply the factor by this value, because titles factors are very low.
FACTOR_ADJUST = 5

TITLES = set(("h1", "h2", "h3", "h4", "h5", "h6"))

class RepeatPattern(RepeatPatternBase):
	"""
	See module documentation
	"""

	def _find_titles(self):
		""" Here I do most of the work.
		1. Find the titles
		2. Get the indices and factors
		3. Break the indices to groups
		4. Populate with the best X titles type
		- There is no need to use "clean_indices" here
		I have to "cheat" with the indices list and the pattern so the factor
		will not be zero. The factor will be low anyway.
		"""
		lst = []
		# Find all titles
		for title, indices in self._items_dict.iteritems():
			# title is coming from repeat_pattern as two-tuple (Tag, index)
			title, index = title
			if not title.tag_name() in TITLES: continue
			try:
				title.level = int(title.tag_name()[1])
			except ValueError:
				title.level = FACTOR_ADJUST
			if self.debug_level > 2:
				print "Found", title
			# "Fix" indices list and pattern
			indices_lst = zip(indices, indices)
			pattern = [title]
			if self.debug_level > 3:
				print "Indices", indices_lst
			factor = self.get_factor(pattern, indices_lst)
			if factor > 0:
				lst.append((pattern, indices_lst, factor))
		return lst

	def _debug_print(self):
		if self.debug_level > 0:
			self._print_pattern("Best %s" % self.num_patterns)

	def process(self, input_lst):
		""" Find the titles """
		self.init(input_lst)
		self.LEN_ONE_MAGIC = None # Cannot use it here, all length=1
		self.min_len = 1 # must be 1 here
		self._items_dict = defaultdict(list) # Dictionary of item: indices
		# Here I'm doing the work
		self._group_items()
		results = self._find_titles()
		if not results: return 0 # We didn't find a pattern
		if self.debug_level > 1:
			print "Titles", results
		# Sort the titles by the factor
		results.sort(key = lambda x: x[2], reverse = True)
		self.gather_occurrences(results, self._debug_print)
		return self.num_patterns

if __name__ == '__main__':
	# TODO: test this module
	pass
