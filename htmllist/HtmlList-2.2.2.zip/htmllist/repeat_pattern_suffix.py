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
This module uses suffix array to find exact repeated patterns in a list.
The logic is pretty much identical to the Suffix Tree logic (in repeat_pattern2),
but the implementation is with suffix array.

The Algorithm:
1. Build a suffix array from the input-list - I use a slightly modified "tools"
	module from the pysuffix project.
2. Add to each item in the suffix-list the number of common elements with the
	previous item. The elements are from the input-list suffix.
3. Repeat for each value (i) from minimum-pattern-length to maximum-common-prefix:
3.1. Group the suffix-list by the condition: if common-elements >= i
3.2. Each True group is a possible pattern, the elements of the group are the
	indices of the pattern (add the last index of the last False group).
3.3. from these indices we need to filter overlaps (every index is a two-tuple
	(start, end), overlap is when the start of an index is before the previous
	index end).

This algorithm is faster then the Suffix Tree algorithm, and takes about half
the memory.

Erez Bibi
2010-05-08
"""

# NOTE: Python 2.6 Only
from collections import namedtuple
# NOTE: Python 2.6 Only
from itertools import izip_longest, izip, groupby

from pysuffix_tools import suffix_array
from repeat_pattern_base import RepeatPatternBase

# Minimum pattern length for this algorithm - it is more sensitive (0 to cancel)
# Now this limit is also a limit for the number of distinct items in the pattern
MIN_LEN_LIMIT = 4

# One item in the suffix tree
SuffixListItem = namedtuple("SuffixListItem", ["index", "prefix"])

class RepeatPattern(RepeatPatternBase):
	"""
	See module documentation.
	"""

	def _print_suffix_array(self, start=0, stop=-1):
		""" Debugging method - Print the suffix list """
		max_len = len(self._suffix_lst)
		if stop == -1: stop = max_len
		for i in xrange(start, stop):
			# Determent how mach of the list data to print.
			a = self._suffix_lst[i].index
			if i < max_len - 1:
				d = max(self._suffix_lst[i].prefix, self._suffix_lst[i+1].prefix)
			else:
				d = self._suffix_lst[i].prefix
			b = min(a + d + 1, max_len)
			print "> %s (%s):\t\t%s ..." % (
				self._suffix_lst[i].index, self._suffix_lst[i].prefix,
				" ".join(repr(item) for item in self._input_lst[a:b]))

	def _print_final(self):
		""" Debug function to pass to gather_occurrences """
		if self.debug_level > 0:
			print "Best %s (Repeats=%s, Factor=%s):" % \
				(self.num_patterns, len(self.indices_lst), self.factor)
			print "\n".join(
				["\t" + str(item) for item in self.pattern])
			if self.debug_level > 1:
				print "Indices List:", self.indices_lst

# ## The next three methods are pretty but are too slow ##
#
# def _sub_lst_itr(self, index):
# 	""" Return an iterator to a suffix of the input_list. The suffix starts
# 	from 'index'.
# 	"""
# 	for i in xrange(index, len(self._input_lst)):
# 		yield self._input_lst[i]
#
# def _compare_sub_lst(self, x, y):
# 	""" Compare two sub lists (suffixes) of the input list. The two suffixes
# 	are starting from indices x and y. The suffixes will not be of the same
# 	length.
# 	"""
# 	for a, b in izip_longest(self._sub_lst_itr(x), self._sub_lst_itr(y)):
# 		val = cmp(a,b)
# 		if val != 0: return val
# 		return 0
#
# def _find_common_prefix(self, x, y):
#	 """ Count how many common item for two sub lists. The sub list
#	 (suffixes) are starting in indices x and y.
#	 """
#	 if x < 0 or y < 0: return 0 # Special case for first item in the list.
#	 itr1 = self._sub_lst_itr(x)
#	 itr2 = self._sub_lst_itr(y)
#	 counter = 0
#	 try:
#	 	while itr1.next() == itr2.next():
#	 		counter += 1
#	 except StopIteration:
#	 	pass
#	 return counter

	## I use these two less pretty but a faster methods instead ##

#	def _compare_sub_lst2(self, x, y):
#		""" Compare two sub lists (suffixes) of the input list. The two suffixes
#		are starting from indices x and y. The suffixes will not be of the same
#		length.
#		"""
#		a, b = sorted((x, y))
#		while b < self.max_index:
#			val = cmp(self._input_lst[a], self._input_lst[b])
#			if val != 0: return val
#			a += 1
#			b += 1
#		return 1 if y > x else -1

	def _find_common_prefix2(self, x, y):
		""" Count how many common items in two sub lists. The sub list
		(suffixes) are starting in indices x and y.
		"""
		if x < 0 or y < 0: return 0 # Special case for first item in the list.
		a, b = sorted((x, y))
		counter = 0
		while b < self.max_index:
			val = cmp(self._input_lst[a], self._input_lst[b])
			if val != 0: break
			counter += 1
			a += 1
			b += 1
		return counter

	def _filter_overlaps(self, indices):
		""" Filter overlapping indices from an indices list """
		new_indices = [indices[0]]
		for i in range(1, len(indices)):
			if indices[i][0] > new_indices[-1][1]:
				new_indices.append(indices[i])
		return new_indices

	def _build_suffix_array(self):
		"""
		Build a suffix array from the input-list (class variable). Every item in
		the array (list) is a two-tuple (index, prefix).
		index is the index of this suffix in the input list.
		prefix is the number of common items with the previous suffix in the
		list.
		"""
		# Suffix list of only indices
		tmp_lst = suffix_array(self._input_lst)
		# Build the real suffix list
		self._suffix_lst = [SuffixListItem(
			tmp_lst[i], self._find_common_prefix2(tmp_lst[i-1], tmp_lst[i])) \
			for i in xrange(len(tmp_lst))]
		self._max_prefix = max(self._suffix_lst, key=lambda x: x.prefix).prefix
		return self._suffix_lst

	def _find_repeat_pattern(self):
		""" Find all possible and acceptable repeat patterns """
		results = []
		if self.max_len:
			self._max_prefix = min(self._max_prefix, self.max_len)
		# Go over all possible pattern lengths
		for pattern_len in range(self.min_len, self._max_prefix + 1):
			# Group by the condition if common prefix is equal or more than the
			# current pattern length, and go over all groups.
			for key, group in groupby(self._suffix_lst,
			key=lambda x: x.prefix >= pattern_len):
				if not key:
					# This is not a group to take but I need the last index in
					# this group - it needs to go into the next (good) group
					for item in group:
						last_index = item.index # TODO: find a better way...
				if key is True:
					# This is a good group, get the indices first
					indices = [item.index for item in group]
					# Get the pattern from the first index
					pattern = self._input_lst[indices[0]:indices[0] + pattern_len]
					if len(set(pattern)) < MIN_LEN_LIMIT: continue
					# Fix indices list
					indices.append(last_index)
					indices.sort()
					indices = [(index, index + pattern_len - 1) for index in indices]
					indices = self._filter_overlaps(indices)
					# And the factor calculation
					factor = self.get_factor(pattern, indices)
					if self.debug_level > 3:
						print "Factor: %s %s" % (factor, pattern)
					if factor > 0:
						if self.debug_level > 2:
							print "Possible: (%s, %s) %s" % (
								len(indices), round(factor, 4), pattern)
						results.append((pattern, indices, factor))
		return results

	def process(self, input_lst):
		"""
		Find repeat patterns in an input-list.
		Returns the number of patterns found.
		"""
		if MIN_LEN_LIMIT and self.min_len < MIN_LEN_LIMIT:
			self.min_len = MIN_LEN_LIMIT
		self.init(input_lst)
		self.max_index = len(input_lst)
		self._build_suffix_array()
		if self.debug_level > 4:
			self._print_suffix_array()
		results = self._find_repeat_pattern()
		if not results: return 0
		results.sort(key = lambda x: x[2], reverse = True)
		return self.gather_occurrences(results, self._print_final)

	## Testing ##

	@classmethod
	def test(cls, verbose=0):
		""" Tests for this class """
		global MIN_LEN_LIMIT
		rp = cls(debug_level=verbose)
		MIN_LEN_LIMIT = 0
		rp.min_repeat = 2
		list1 = list('XYZXYZABCkABClABCmABCXYZ') # ABC better then XYZ
		list2 = list('ABCAYBCAXBC') # Cannot take ABC take BC

		if verbose: print list1
		rp.max_patterns = 5
		rp.process(list1)
		assert rp.pattern == ['A', 'B', 'C'], rp.pattern
		assert rp.indices_lst == [(6, 8), (10, 12), (14, 16), (18, 20)], rp.indices_lst
		# Test multiple patterns
		rp.pattern_num = 1
		assert rp.pattern == ['X', 'Y', 'Z'], rp.pattern
		rp.pattern_num = 0
		rp.sort(rp.INDICES)
		assert rp.pattern == ['X', 'Y', 'Z'], rp.pattern
		if verbose: print "----------------------------------------------"

		if verbose: print list2
		rp.process(list2)
		assert rp.pattern == ['B', 'C'], rp.pattern
		assert rp.indices_lst == [(1,2), (5,6), (9,10)], rp.indices_lst
		rp.process_by_pattern(list('YBCA'))
		assert rp.repeats == 1, rp.repeats
		if verbose: print "----------------------------------------------"

if __name__ == '__main__':
	RepeatPattern.test(verbose=4)
	print "Test Passed"

	text = """make an iterator that aggregates elements from each of the
	iterables if the iterables are of uneven length missing values are
	filled-in with fillvalue iteration continues until the longest iterable is
	exhausted
	aaa aaa aaa aaa aaa aaa aaa"""
