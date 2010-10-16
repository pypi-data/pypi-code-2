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
This module tries to assess the quality of a pattern on an HTML page. It has
more information than the RepeatPattern classes because it sees the HTML page
itself (through the BreakHtmlPage class).

The only "public" function is "pattern_quality" that takes RepeatPattern object
and BreakHtmlPage object and returns a number between 0 and 1. The higher the
number the better the quality.

The current implementation checks the deviation of the number of words and the
number of tags in each section of a pattern in each occurrences. But in the
future I may change this assessment without having to change the usage of this
module.
"""

from tag_tools import Tag

def _print_matrix(matrix):
	""" Debugging function """
	for i in range(len(matrix)):
		print '\t'.join(str(elm) for elm in matrix[i])

def _deviation(lst):
		""" Return an inverse normalized deviation in a list of numbers.
		lst - A list of numbers
		Returns a number between 0 and 1 (1 = no deviation)
		"""
		if not lst: return 0
		length = len(lst)
		avg = float(sum(lst)) / length
		max_dev = max(lst) - min(lst)
		if max_dev == 0: return 1
		sum_dev = sum(map(lambda x: abs(x-avg), lst))
		return 1 - ((sum_dev / length) / max_dev)

def _avrg_deviation(matrix):
	""" Calculates the average normalized deviation on the matrix rows.
	"""
	devs = [_deviation(row) for row in matrix]
	if not devs: return 0
	return sum(devs) / len(devs)

def _is_elm_tag(elm, tag, bhp):
	""" Compare between an Element (from break_html_page) and a tag (from
	tag_tools)
	"""
	if bhp.get_element_name(elm) != tag.tag_name():
		return False
	return tag == Tag(*bhp.get_all_element_data(elm))

def _fill_matrix(rp, bhp, words_matrix, tags_matrix):
	""" This is a coroutine that fills two matrixes. The number of words between
	pattern tags, and the number of tags between pattern tags. It gets elements,
	and add a values to the matrixes every time the element is a tag from the
	pattern.
	"""
	counter = 0
	tags_counter = 1
	last_elm = elm = (yield)
	try:
		while counter < len(rp.pattern) - 1:
			tag = rp.pattern[counter+1]
			elm = (yield)
			if _is_elm_tag(elm, tag, bhp):
				# Found a tag
				words_matrix[counter].append(
					bhp.words_between_elements(last_elm, elm))
				tags_matrix[counter].append(tags_counter)
				last_elm = elm
				tags_counter = 0
				counter += 1
			tags_counter += 1
		while True:	# This is for the section after the last tag in the pattern
			elm = (yield)
			tags_counter += 1
	except GeneratorExit: # And add the last section value
		words_matrix[counter].append(bhp.words_between_elements(last_elm, elm))
		tags_matrix[counter].append(tags_counter)

def pattern_quality(rp, bhp):
	""" Access a pattern quality on an HTML page.
	rp - RepeatPattern object.
	bhp - BreakHtmlPage object
	Return a number between 0 to 1, the higher the number the better the quality.
	"""
	# Every column in the matrix is the number of "words" after each tag from
	# the pattern. Every row is a specific occurrence of the pattern (index).
	matrix_words = [[] for _ in range(len(rp.pattern))]
	matrix_tags = [[] for _ in range(len(rp.pattern))]
	for elm_lst, next in bhp.get_text_list(rp.indices_lst):
		# Create a coroutine
		elm_func = _fill_matrix(rp, bhp, matrix_words, matrix_tags)
		elm_func.next() # Init it
		bhp.traverse_list(elm_lst, elm_func.send, elm_func.send, stop_elm=next)
		elm_func.close() # Close the coroutine
	#print "TAGS"
	#_print_matrix(matrix_tags)
	#print ">>>", _avrg_deviation(matrix_tags)
	#print "WORDS"
	#_print_matrix(matrix_words)
	#print ">>>", _avrg_deviation(matrix_words)
	return (_avrg_deviation(matrix_tags) + _avrg_deviation(matrix_words)) / 2.0

