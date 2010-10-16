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
This simple RepeatPattern class is similar to the one in the repeat_title module.
It inherit from RepeatPattern from the repeat_pattern module (Count Tags algo).
The class looks at some container (grouping) tags from the list, and expands them
using the _expand_bucket method of the Count Tags algorithm. It then takes the
patterns with the best factor.

It works surprisingly well but tend to yield patterns that overlaps (different
patterns not different occurrences of one pattern). So it is better to get only
the first pattern from this class.

The constructor of this class takes an optional argument "tags" that has to be a
tag_tools.TagSet object. These are the tags to look at. If this argument is
missing, the class will look at a default list of tags.
"""

from collections import defaultdict

from repeat_pattern import RepeatPattern as RepeatPatternBase
from tag_tools import CONTAINER_TAGS

class RepeatPattern(RepeatPatternBase):
	"""
	See module documentation
	"""

	def __init__(self, tags=None, *args, **kw):
		RepeatPatternBase.__init__(self, *args, **kw)
		if tags:
			self._group_tags = tags
		else:
			self._group_tags = CONTAINER_TAGS

	def _find_group_tags(self):
		""" Here I do most of the work.
		1. Find all grouping tags.
		2. Expand around the tag.
		3. Add to list if factor is not zero.
		"""
		lst = []
		# Find all grouping tags
		for tag, indices in self._items_dict.iteritems():
			# A tag is coming from repeat_pattern as two-tuple (Tag, index)
			tag, index = tag
			if not tag in self._group_tags: continue
			# Grouping tag has attributes and in the Grouping Tags set
			if self.debug_level > 2:
				print "Found:", tag
			# "Fix" indices list and pattern
			indices_lst = zip(indices, indices)
			pattern = [tag]
			if len(indices_lst) > 1: # Expand pattern
				indices_lst = self._expand_bucket(
					pattern, indices_lst, after_only=True)
			if self.debug_level > 3:
				self._print_list("Indices", indices_lst)
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
		results = self._find_group_tags()
		if not results: return 0 # We didn't find a pattern
		if self.debug_level > 1:
			self._print_list("Grouping Tags", results)
		# Sort the titles by the factor
		results.sort(key = lambda x: x[2], reverse = True)
		self.gather_occurrences(results, self._debug_print)
		return self.num_patterns

if __name__ == '__main__':
	# TODO: test this module
	pass
