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
Another way to find the repetitive pattern - This is the "new" algorithm.

This algorithm is based on the heuristic assumption that the pattern we are
looking for will have some items (tags) that will appear only in it. It is not
true for the mathematical representation of the problem, but will be true in
many real world case (HTML pages)

1. count the number of occurrences for each item and build an indices list
1.1 break each indices list to sub lists so each sub list will be within the
	STDV limit - This makes the heuristic assumption true in many more cases.
2. sort by number of occurrences (keep original order when possible)
3. group by counter (put in "buckets") - consider also different sequences
	within the same counter value*
4. find the best bucket (bucket factor is higher)
5. try to expand the bucket as much as possible (see _expand_bucket)

* For each item we are keeping a list of indices.
We should group items by the length of the indices list (number of occurrences)
BUT every such group (bucket) should only hold items that their indices form a
repetitive sequence. So each index of a new item in a bucket should be larger
than the last item index but smaller then the next index of the first item.
In other words, there may be more than one bucket for each number of occurrences
value.

Important to note: I always keep the original order of the items. In every
sub-items list, the order of the items will be as it is in the original input
list (first occurrence of the item). Also, every indices list will be sorted
that way.

Erez Bibi
2009-11-6
"""

from collections import defaultdict

from repeat_pattern_base import RepeatPatternBase

# When expanding a pattern, the algorithm looks for common tags in a window of
# this width
EXPANSION_LOOK_AHEAD = 2

class RepeatPattern(RepeatPatternBase):
	"""
	See module documentation
	"""

	## Debugging Methods ##

	def _print_dict(self, name, dic):
		print name, ':'
		for key, val in dic.iteritems():
			print '\t', key, ':', val

	def _print_list(self, name, lst):
		print name, ':'
		for itm in lst:
			print '\t', itm

	def _print_pattern(self, name):
		self._print_list("%s (Repeats=%s, Factor=%s)" % \
			(name, self.repeats, self.factor), self.pattern)

	def _print_final(self):
		if self.debug_level > 0:
			self._print_pattern("Best %s" % self.num_patterns)

	## Buckets help methods ##

	def _is_in_bucket(self, item, bucket):
		""" Check if an item (indices-list) belong to the sequence that exists in
		this bucket. The new indices list must be after the last one, but before
		the next index of the first list.
		"""
		first_indices = self._items_dict[bucket[0]]
		last_indices = self._items_dict[bucket[-1]]
		new_indices = self._items_dict[item]
		length = len(first_indices) # all lists are the same length
		# Make sure all new items are in appropriate places,
		# last item is special case
		return all(new_indices[i] > last_indices[i] and \
			(i == length - 1 or new_indices[i] < first_indices[i+1]) \
			for i in range(length))

	@staticmethod
	def clean(pattern):
		""" The items I store in the buckets may be two-tuples (Tag, index) or
		plain Tags. This method returns the bucket to ALL Tags state.
		"""
		return [item[0] if isinstance(item, tuple) else item for item in pattern]

	## Expanding methods ##

	def _is_indices_ok(self, indices):
		""" Check that there is no overlapping in the indices list """
		if indices[0][0] < EXPANSION_LOOK_AHEAD:
			return False
		if indices[-1][1] > len(self._input_lst) - EXPANSION_LOOK_AHEAD:
			return False
		return all(indices[i][1] < indices[i+1][0] for i in \
			range(len(indices)-1))

	# TODO: Optimize this method (?)
	def _find_common_item(self, lst_lst):
		""" Find a common item in a list of lists.
		Return a two-tuple: the list of indices of the common item in every
		sub-list, and the common item itself.
		If there is no common item it returns (None, None)
		"""
		if not lst_lst: return None, None
		for index, itm in enumerate(lst_lst[0]):
			ret_lst = [index+1]
			for lst in lst_lst[1:]:
				try:
					index = lst.index(itm)
				except ValueError:
					break
				ret_lst.append(index+1)
			if len(ret_lst) == len(lst_lst):
				return ret_lst, itm
		return None, None

	def _expand_bucket(self, pattern, indices, after_only=False):
		""" This method will try to expand a bucket (pattern, indices) as much
		as possible. 'indices' is a list of two-tuple (start, end) of the
		indices of 'pattern'.
		It expands first the end of the indices, and then the beginning of it.
		It stops when there is no more possible expansion, or when farther
		expansion will corrupt the indices list (cause overlapping).

		When looking for an item to add, it looks in windows of
		EXPANSION_LOOK_AHEAD places in the input-list (before the start index or
		after the end index), if it finds a common item in these windows, it
		will try to expand the indices list to include this item (and add the
		item to the pattern).

		after_only is an optional flag to expand only after the pattern.

		Returns the new indices list
		Change the pattern list in place!
		"""
		before_ok = after_ok = True
		new_items = 0
		# Try to find common items AFTER the pattern
		while after_ok:
			items = [list(self._input_lst[i+1:i + EXPANSION_LOOK_AHEAD + 1]) for \
				_,i in indices]
			expansion, itm = self._find_common_item(items)
			if expansion:
				tmp_indices = [(s_e[0],s_e[1]+expansion[index]) for \
					index, s_e in enumerate(indices)]
				if self._is_indices_ok(tmp_indices):
					new_items += 1
					indices = tmp_indices
					pattern.append(itm)
				else: after_ok = False
			else: after_ok = False
		# Try to find common items BEFORE the pattern
		while before_ok and not after_only:
			items = [list(reversed(self._input_lst[i - EXPANSION_LOOK_AHEAD:i])) \
				for i,_ in indices]
			expansion, itm = self._find_common_item(items)
			if expansion:
				tmp_indices = [(s_e[0]-expansion[index],s_e[1]) for \
					index, s_e in enumerate(indices)]
				if self._is_indices_ok(tmp_indices):
					new_items += 1
					indices = tmp_indices
					pattern.insert(0, itm)
				else: before_ok = False
			else: before_ok = False
		return indices

	## First level private methods ##

	def _group_items(self):
		""" Create an indices list for each item in the input list.
		It breaks the indices lists so they will be under the maximum STDV of
		the system. So each item may have more than one indices list.
		"""
		for index, item in enumerate(self._input_lst):
			self._items_dict[item].append(index)
		tmp_dict = {}
		for item, indices in self._items_dict.iteritems():
			for counter, indices_lst in enumerate(
			 self.break_indices_lst(indices, two_tuple=False)):
				if indices_lst:
					# TODO: Maybe find better marking for groups of items...
					tmp_dict[(item, counter)] = indices_lst
		self._items_dict = tmp_dict
		if self.debug_level > 4: self._print_dict("Items:", self._items_dict)
		return self._items_dict

	def _put_in_buckets(self):
		""" Distribute the items to buckets according to the number of
		occurrences. There is a second level of distribution (to buckets) by
		different "sequences" in the same first level bucket. A sequence is
		created by items that appear one after the other in the same order.
		"""
		item_indices = self._items_dict.items()
		# Here I filter out indices list that are too short
		item_indices = filter(lambda x: len(x[1]) >= self.min_repeat and (
			not self.max_repeat or len(x[1]) <= self.max_repeat), item_indices)
		# First level of distribution to buckets is by length of indices list
		# I also sort by the first index to preserve the original order in each
		# bucket
		item_indices.sort(key = lambda x: (len(x[1]), x[1][0]))
		# Put items in the buckets and create the second level of distribution
		for item, indices in item_indices:
			new_bucket = True
			for bucket in self._buckets_dict[len(indices)]:
				if self._is_in_bucket(item, bucket):
					bucket.append(item)
					new_bucket = False
					break
			if new_bucket: # Create new bucket with it's first item
				self._buckets_dict[len(indices)].append([item])
		if self.debug_level > 3: self._print_dict("Backets", self._buckets_dict)
		return self._buckets_dict

	def _find_best_bucket(self):
		""" Find the best buckets, or in other words the best patterns in the
		input list. A bucket is a list of items that repeat same number of times
		and creates a sequence.
		After this method returns:
			self.factor Will hold the best buckets factor (list)
			self.pattern Will hold the best patterns (list)
			self.indices_lst Will hold a list of lists of two-tuple, indices of
				the best pattern (start, end).
			self.repeats Will hold the number of occurrences of the best patterns
		Before finding the best buckets it tries to expand them.
		"""
		# Flatten the list of buckets (dict of lists), and get the factor and
		# length for each one
		patterns = [bucket for buckets in self._buckets_dict.itervalues() \
			for bucket in buckets]
		if self.debug_level > 2: self._print_list("Pre-Factors", patterns)
		lst = []
		# Find and expand all patterns
		for pattern in patterns:
			indices = zip(
				self._items_dict[pattern[0]], self._items_dict[pattern[-1]])
			pattern = self.clean(pattern)
			factor = self.get_factor(pattern, indices)
			if factor > 0:
				if len(indices) > 1: # Expand pattern
					indices = self._expand_bucket(pattern, indices)
					factor = self.get_factor(pattern, indices)
				lst.append((pattern, indices, factor))
		if not lst: return 0 # We didn't find a pattern
		# Sort the buckets by the factor
		lst.sort(key = lambda x: x[2], reverse = True)
		if self.debug_level > 1:
			self._print_list("Expanded Patterns and Factors",
				[(itm[0], itm[2]) for itm in lst])
		return self.gather_occurrences(lst, self._print_final)

	## Public Methods ##

	@property
	def relevant_items(self):
		""" A list of items that might be useful to other algorithms
		"""
		if not hasattr(self, "_buckets_dict"): return None
		return (item for bucket in self._buckets_dict.itervalues() \
			for items in bucket for item in items)


	def process(self, input_lst):
		""" Find the best patterns in a list of items (see module documentation
		for more details).
		Returns the number of patterns found
		"""
		self.init(input_lst)
		self._items_dict = defaultdict(list) # Dictionary of item: indices
		self._buckets_dict = defaultdict(list)
		# Here I'm doing the work
		self._group_items()
		self._put_in_buckets()
		if not self._buckets_dict: return 0
		self._find_best_bucket()
		return self.num_patterns


	## Testing ##

	@classmethod
	def test(cls, verbose=0):
		""" Tests for this class """
		rp = cls(debug_level=verbose)
		rp.min_repeat = 2
		list1 = list('XYKaLbKcLdKeLXY') # "KL" is better then "XY"
		list2 = list('gibrishAXBCAYBCAXYBCAYXBCABChsirbig') # "ABC" drop X and Y
		list3 = list2 + ['B'] # This will drop also the B
		list4 = list('ABCDEFGHIJKLMNOP') # No pattern
		list5 = list('babaaXYbaXYbaXYbabab')# Expandable pattern
		list6 = list('aABCbABCcdXYZefXYZghDEFiDEFj') # Weight: XYZ is better then ABC or DEF
		list7 = list('ABC') + list6 # Multiple patterns

		if verbose: print list1
		rp.process(list1)
		assert rp.indices_lst == [(2,4), (6,8), (10,12)], rp.indices_lst
		assert rp.pattern == ['K', 'L'], rp.pattern
		rp.process_by_pattern(list('bKcLd'))
		# Lazy mode test
		assert rp.repeats == 1, rp.repeats
		#assert rp.factor == 6, rp.factor # Equal distances between items
		if verbose: print "----------------------------------------------"

		if verbose: print list2
		rp.process(list2)
		assert rp.pattern == ['A', 'B', 'C'], rp.pattern
		# Distances between items are not equal
		#assert rp.factor < len (rp.pattern) * rp.repeats
		if verbose: print "----------------------------------------------"

		if verbose: print list3
		rp.process(list3)
		assert rp.pattern == ['A', 'C'], rp.pattern
		if verbose: print "----------------------------------------------"

		if verbose: print list4
		rp.process(list4)
		assert rp.pattern is None, rp.pattern
		#rp.min_repeat = 1 # with no limit on number of repeats there is a much
		#rp.process(list4)
		#assert rp.pattern, rp.pattern
		#assert rp.repeats == 1, rp.repeats
		if verbose: print "----------------------------------------------"
		rp.min_repeat = 2

		if verbose: print list5
		# Expandable - Should add 'a' before and 'b' after the pattern
		rp.process(list5)
		assert rp.pattern == ['X', 'Y', 'b', 'a'], rp.pattern
		if verbose: print "----------------------------------------------"

		if verbose: print list6
		# Pattern Weight
		rp.process(list6)
		assert rp.pattern == ['X', 'Y', 'Z'], rp.pattern
		if verbose: print "----------------------------------------------"

		if verbose: print list7
		# Multiple patterns
		# TODO: Should XYZ come before ABC?
		rp.max_patterns = 5
		rp.process(list7)
		assert rp.pattern == ['X', 'Y', 'Z'], rp.pattern
		rp.pattern_num = 1
		assert rp.pattern == ['A', 'B', 'C'], rp.pattern
		assert rp.repeats == 3, rp.repeats
		rp.pattern_num = 2
		assert rp.pattern == ['D', 'E', 'F'], rp.pattern
		assert rp.repeats == 2, rp.repeats
		try:
			rp.pattern_num = 3
			assert False
		except IndexError: pass
		rp.pattern_num = 0
		# Test resorting
		rp.sort(rp.INDICES)
		assert rp.pattern == ['A', 'B', 'C'], rp.pattern
		assert rp.repeats == 3, rp.repeats


if __name__ == '__main__':
	RepeatPattern.test(4)
	print "Test Passed"

