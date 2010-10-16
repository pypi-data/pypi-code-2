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
This is a base class for all algorithms of the repeat-pattern classes.
It defines some common help methods and the classes interface.

I use two measurements for the pattern quality from the IEPAD paper
(http://portal.acm.org/citation.cfm?id=372182), Coverage and Compactness it is
working like a charm :) The Regularity measurement is identical to my nstdv
method. In addition I am using "weight" (see the method doc).

The basic usage is something like:
	>>> rp = RepeatPattern()
	>>> rp.process(input_list)
	>>> print "The best pattern is:", rp.pattern
	>>> print "Indices of the pattern:", rp.indices_lst

This class is finding and returning multiple patterns. It is an iterator over
the patterns. When working with multiple patterns we need to set the
configuration parameter "max_patterns" to a number bigger then one. In order to
get the patterns do something like:

	>>> if rp.process(lst):
	>>> 	for i in rp:
	>>> 		print rp.pattern
	>>> 		print rp.indices_lst

* And there is also a sort method:

	>>> rp.sort(rp.INDICES) # First pattern first
	>>> rp.sort(rp.PATTERN) # Longest pattern first
	>>> rp.sort(rp.REPEATS) # Prevalent pattern first
	>>> rp.sort(rp.FACTOR)  # best pattern first (the default)

There is also an option to work in a "lazy" mode when processing many pages from
the same source.

	>>> rp = RepeatPattern()
	>>> rp.process(input_list)
	For another page with the SAME format (new input_list)
	>>> rp.process_by_pattern(new_input_list)
	>>> print rp.indices_lst # rp.pattern will not change

The methods "get_factor", "clean_indices", "break_indices_lst" and
"gather_occurrences" are for the RepeatPattern sub-classes use, but not for the
end user (kind of protected). For usage example see repeat_pattern.py (or any
other algorithm module).
"""

# NOTE: Python 2.6 Only
from abc import ABCMeta, abstractmethod
# NOTE: Python 2.6 Only
from collections import Iterable
import math

from tag_tools import CONTAINER_TAGS, Tag

# Factor "penalty" if the pattern doesn't start with a container tag
CONTAINER_PENALTY = 0.5

class RepeatPatternBase(Iterable):
	"""
	Base class for the RepeatPattern classes (see module documentation).
	"""

	__metaclass__ = ABCMeta

	## Fields Constants ##
	PATTERN = 0
	INDICES = 1
	FACTOR = 2
	REPEATS = 3 # I need it for sorting but it is not a real matrix field

	NUM_FIELDS = 3

	# "length one magic" is a rule that say: If the number of items in the
	# pattern is one, the STDV must be below a special minimum (the value of
	# this flag). Set to None to disable this "magic".
	LEN_ONE_MAGIC = 0

	def __init__(self, min_len=2, max_len=0, min_repeat=2, max_repeat=0,
		max_stdv=1, min_weight=0, min_coverage=0, min_comp=0,
		max_patterns=1, debug_level=0):
		""" Configuration Parameters:
		min_len - Optional minimum length of the output pattern (sub-list),
			default = 2
		max_len - Optional maximum length of the output pattern (sub-list),
			default = 0 which is no limit.
		min_repeat - Optional minimum time the pattern should repeat in the list,
			default = 2.
			Note: min_repeat must be more then one!
		max_repeat - Optional maximum time the pattern should repeat in the list,
			a value of zero cancels this limit, default = 0.
		max_stdv - Optional maximum normalized standard deviation of the
			distances between occurrences. This is a number between 0 and 1.
			0 means that the occurrences are in sequence (no other item in
			between). 1 means that there is no importance to the position of the
			occurrences in the list. The default is one.
		min_weight - Optional minimum weight of the occurrences list (see the
			_weight method), a value of zero cancels this limit, default = 0.
		min_coverage - Optional minimum coverage of the occurrences list (see
			the _coverage method), a value of zero cancels this limit,
			default = 0.
		min_comp - Optional minimum compactness of the occurrences list (see the
			_compactness method), a value of zero cancels this limit, default = 0.
		max_patterns - Optional maximum number of possible patterns to find. The
			default is one.
		debug_level - Print debugging messages. A number between 0 (none)
			and 5 (all)
		All parameters can be also controlled by changing class members with the
		same names.
		"""
		## Configuration Parameters ##
		self.min_len = min_len
		self.max_len = max_len
		self.min_repeat = min_repeat
		self.max_repeat = max_repeat
		self.max_stdv = max_stdv
		self.min_weight = min_weight
		self.min_coverage = min_coverage
		self.min_comp = min_comp
		self.max_patterns = max_patterns
		self.debug_level = debug_level
		self.init()

	def init(self, input_lst=None):
		""" Initialize this instance (may be called more than once) """
		## Input ##
		self._input_lst = input_lst

		## Internal ##
		self._matrix = [] # A list of lists that holds the results
		self._num_patterns = 0 # Number of possible patterns found.
		self._pattern_num = None # The pattern that we are working with

	def __iter__(self):
		""" Iterate over patterns when working with multiple patterns.
		This iterator has side effects, so nesting iteration will not work.
		"""
		for i in range(self._num_patterns):
			self._pattern_num = i
			yield i

	############################################################################

	## Pattern Factor Calculating Methods ##

	def _derivative(self, lst, order=1):
		""" This method performs discrete derive on a list of numbers. This is
		the list of gaps between the numbers of the list.
		order - the derive order.
		Returns a list of numbers or an empty list
		"""
		new_lst = lst
		while order:
			if len(lst) < 2: return []
			new_lst = [abs(lst[i+1] - lst[i]) for i in range(len(new_lst) - 1)]
			order -= 1
		return new_lst

	def _nstdv(self, lst):
		""" This method calculates a normalized standard deviation on a list of
		numbers. It calculates a regular standard deviation and then divides it
		by the maximum of the list, the result should be equal or greater than
		zero but less than one.
		"""
		if not lst: return 0
		length = len(lst)
		avg = float(sum(lst)) / length
		sqr_sum = float(sum(map(lambda x: x*x, lst)))
		stdv = math.sqrt((sqr_sum / length) - (avg * avg))
		return stdv / max(lst)

	def _weight(self, indices):
		""" The weight of a pattern is the distance between the middle index of
		the input-list and the average index of the pattern's span.
		The weight is normalized to be between 0 and 1. The closer the distance
		the higher the weight.

		In an HTML page the most important list should be near the middle of the
		rendered page, and that imply in many cases the middle of the HTML tags
		list. It is a questionable assumption but it seems to prevent picking a
		menu list in the top or left of a page.
		"""
		half_len = len(self._input_lst) / 2.0
		avg_index = float(sum((end + start) / 2.0 for start, end in indices)) \
			/ len(indices)
		weight = 1 - (abs(half_len - avg_index) / half_len)
		return weight

	def _coverage(self, indices):
		""" Measures the volume of content in a pattern, that is how much of the
		input list this pattern spans.
		Taken form the IEPAD paper.
		"""
		coverage = float(indices[-1][1] - indices[0][0]) / len(self._input_lst)
		return coverage

	def _compactness(self, pattern, indices):
		""" Measure of the density of a pattern. It can be used to eliminate
		patterns that are scattered far apart beyond a given bound.
		Taken form the IEPAD paper.
		"""
		if len(indices) < 2: return 0
		return float(len(indices) * len(pattern)) / \
			(indices[-1][1] - indices[0][0])


	############################################################################

	## Properties ##

	@property
	def num_patterns(self):
		""" Number of patterns found """
		return self._num_patterns

	@num_patterns.setter
	def num_patterns(self, value):
		""" Prepare place to this number of patterns
		Always has to be set before working with the other properties.
		Also set pattern_num to be the last pattern.
		"""
		if value > self._num_patterns:
			self._matrix.extend([None] * self.NUM_FIELDS for \
				i in range(value - self._num_patterns))
		self._num_patterns = value
		self._pattern_num = value - 1

	@property
	def pattern_num(self):
		""" The number (index) of the pattern we are dealing with
		Must be between 0 and patterns_num
		"""
		return self._pattern_num

	@pattern_num.setter
	def pattern_num(self,value):
		""" Setting this value has the same effect as iterating through this
		RepeatPattern object.
		"""
		if value < 0 or value >= self._num_patterns:
			raise IndexError("Pattern number out of range")
		self._pattern_num = value

	# These properties hide the fact we are working with multiple patterns
	# From the sub classes

	@property
	def pattern(self):
		""" The Pattern """
		if not self._matrix:
			return None
		return self._matrix[self._pattern_num][self.PATTERN]

	@pattern.setter
	def pattern(self, value):
		self._matrix[self._pattern_num][self.PATTERN] = value

	@property
	def indices_lst(self):
		""" The places the pattern occur in the input list """
		if not self._matrix:
			return None
		return self._matrix[self._pattern_num][self.INDICES]

	@indices_lst.setter
	def indices_lst(self, value):
		self._matrix[self._pattern_num][self.INDICES] = value

	@property
	def factor(self):
		""" The factor of this pattern """
		if not self._matrix:
			return None
		return self._matrix[self._pattern_num][self.FACTOR]

	@factor.setter
	def factor(self, value):
		self._matrix[self._pattern_num][self.FACTOR] = value

	@property
	def repeats(self):
		""" The number of occurrences of this pattern in the input list.
		This is a "virtual" property, I return the indices list length.
		"""
		if not self._matrix:
			return None
		return len(self._matrix[self._pattern_num][self.INDICES])

	@repeats.setter
	def repeats(self, value):
		""" Ignore it - we will take repeats from len(indices) """
		pass

	############################################################################

	## Public Methods ##

	@abstractmethod
	def process(self, input_lst):
		""" Find the best patterns in a list of items.
		Returns the number of patterns found.

		A derived class MUST implement this method.
		"""

	def process_by_pattern(self, input_lst):
		""" Find the indices list in a "lazy" mode from a pattern we already
		found. This method will not be relevant in most cases. It can be used to
		process multiple pages from the same source, and will work also if the
		indices list is shorter than "min_repeat".

		The method do a brute-force search on the input-list. Remember that
		there might be gaps between the pattern items.
		Return the number of patterns found.
		"""
		# TODO: Is it really working in all cases?
		n = len(input_lst)
		d = len(self.pattern)
		pattern_set = set(self.pattern) # For quick search
		self.indices_lst = []
		self.repeats = 0
		i = j = 0 # i - input list index, j - pattern index
		while i < n:
			if input_lst[i] == self.pattern[j]: # One item match
				if j == 0: # This is the first item
					start = i
				j += 1
			elif input_lst[i] in pattern_set: # Need to start over
				if input_lst[i] == self.pattern[0]:
					start = i
					j = 1
				else:
					j = 0
			i += 1
			if j == d: # Found one
				self.indices_lst.append((start, i-1))
				self.repeats += 1
				j = 0
		return self.repeats

	def sort(self, sort_by=FACTOR):
		""" Sort the result pattern by a specific field (and rule) """
		if sort_by == self.PATTERN:
			key = lambda x: len(x[sort_by])
			reverse = True
		elif sort_by == self.INDICES:
			key = lambda x: x[sort_by][0]
			reverse = False
		elif sort_by == self.FACTOR:
			key = lambda x: x[sort_by]
			reverse = True
		elif sort_by == self.REPEATS:
			key = lambda x: len(x[self.INDICES])
			reverse = True
		else:
			raise TypeError(
				"sort_by must be one of RepeatPatternBase fields constants")
		self._matrix.sort(key=key, reverse=reverse)

	############################################################################

	## "Protected" Methods ##

	def get_factor(self, pattern, indices, print_data=False):
		""" Calculate factor for a repetitive pattern.
		pattern - a list of items.
		indices - The occurrences of this pattern, a list of (start, end) indices.

		Return 0 if the pattern should not be considered or the pattern factor.
		"""
		# General limits
		repeats = len(indices)
		ptrn_len = len(pattern)
		if repeats < self.min_repeat: return 0
		if self.max_repeat and repeats > self.max_repeat: return 0
		if ptrn_len < self.min_len: return 0
		if self.max_len and ptrn_len > self.max_len: return 0
		# Regularity = STDV
		regularity = self._nstdv(self._derivative([index[0] for index in indices]))
		if regularity > self.max_stdv: return 0
		if not self.LEN_ONE_MAGIC is None and \
		 len(pattern) == 1 and regularity > self.LEN_ONE_MAGIC:
			return 0
		# Other Factors
		weight = self._weight(indices)
		if self.min_weight and weight < self.min_weight: return 0
		coverage = self._coverage(indices)
		if self.min_coverage and coverage < self.min_coverage: return 0
		compactness = self._compactness(pattern, indices)
		if self.min_comp and compactness < self.min_comp: return 0
		# Give priority to patterns that starts with a container tag
		# The isinstance test is for not breaking the test methods (I need to
		# think about it)
		container = 1 if not isinstance(pattern[0], Tag) or \
			pattern[0] in CONTAINER_TAGS else CONTAINER_PENALTY

		factor = (1 - regularity)  * weight * coverage * compactness * container
		if print_data:
			print "Factor: %s\n\tRegularity: %s\n\tWeight: %s\n\tCoverage: %s\n\tCompactness: %s" \
				% (factor, regularity, weight, coverage, compactness)
		return factor

	def clean_indices(self, indices):
		""" Remove indices that are included in other indices in the matrix
		(from all patterns from all indices).
		Change the 'indices' list in place!
		Returns the length of the modified indices list.
		"""
		# TODO: Optimize if possible.
		def _overlap(index):
			#return any(index[0] >= ind[0] and index[0] <= ind[1] or \
			# index[1] >= ind[0] and index[1] <= ind[1] \
			# for ind in self.indices_lst)
			for ind in self.indices_lst:
				if ind[1] > index[0] and ind[0] < index[1]:
					return True
			return False

		removables = []
		for i, index in enumerate(indices):
			for x in self:
				if _overlap(index):
					removables.append(i)
					break

		for i in reversed(removables):
			del indices[i]
		return len(indices)

	def break_indices_lst(self, indices, two_tuple=True):
		""" Break a list of indices to a list of lists of indices, so all indices
		lists will be within the STDV limit. All the lists will also be within
		the length limit. It ignores the LEN_ONE_MAGIC rule.
		two_tuple is an optional flag to indicate that every item in the list is
		a single number (set to False, default is two_tuple)
		A side effect of this method is the removal of indices-lists shorter than
		the minimum.
		This is a recursive method.
		Returns a list of indices lists.
		"""
		if len(indices) < self.min_repeat: return [] # First base case
		if two_tuple:
			tmp_lst = [start for start, _ in indices]
		else:
			tmp_lst = indices
		der_lst = self._derivative(tmp_lst)
		stdv = self._nstdv(der_lst)
		if stdv < self.max_stdv: # I ignore LEN_ONE_MAGIC
			return [indices] # Second base case
		max_gap = max(der_lst)
		for index, val in enumerate(der_lst):
			if max_gap == val:
				return \
				self.break_indices_lst(indices[:index+1], two_tuple=two_tuple) +\
				self.break_indices_lst(indices[index+1:], two_tuple=two_tuple)

	def gather_occurrences(self, results, dbg_func=None):
		"""
		The final occurrences gathering method.
		results is a three-tuple (pattern, indices, factor)
		dbg_func is an optional debugging function.

		This method populates this object with the chosen patterns.
		Returns the number of patterns gathered
		"""
		self.num_patterns = 0
		index = 0
		# Extract and work on the best patterns
		while self.num_patterns < self.max_patterns and index < len(results):
			pattern, indices, factor = results[index]
			old_len = len(indices)
			new_len = self.clean_indices(indices)
			if new_len >= self.min_repeat:
				if new_len < old_len: # Factor has changed
					factor = self.get_factor(pattern, indices)
				if factor > 0:
					self.num_patterns += 1 # Also sets the new pattern as "active"
					self.pattern = pattern
					self.indices_lst = indices
					self.factor = factor
					if dbg_func:
						dbg_func()
						# Uncomment to print factor data
						#self.get_factor(pattern, indices, print_data=True)
			index += 1
		self.sort()
		if self.num_patterns:
			self.pattern_num = 0
		return self.num_patterns

	############################################################################

	## The two following methods initialize an object from another object ##

	def get_pattern(self):
		""" """
		return self.pattern

	def set_pattern(self, lst):
		""" """
		self.pattern = lst

