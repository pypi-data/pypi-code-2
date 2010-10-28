#!/usr/bin/env python

"""This module lets you search through label files
to find particular ngrams."""


__version__ = "$Revision: 1.7 $"

# from xwaves_errs import *

import re
import xwaves_mark
import xwaves_lab
from xwaves_errs import *


WildAnyOne = re.compile('.')

def matches(data, pattern):
	if len(data) != len(pattern):
		return 0
	for (d, p) in zip(data, pattern):
		if hasattr(p, 'match'):
			if not p.match(d):
				return 0
		elif d != p:
			return 0
	return 1
	

def find_mark(ngram, fname, datatype=xwaves_mark.PHONE):
	"""ngram = list of labels.
	fname = file name for xwaves_mark datafile.
	datatype = xwaves_mark.PHONE or xwaves_mark.WORD
	
	This function returns all instances
	(even overlapping instances) of the specified
	N-gram in the file.  The return format
	is [ (end_time, label), ... ],
	where the zeroth entry in the list is the
	symbol before the start of the N-gram.
	It's end time is the beginning of the N-gram.

	In the argument list, the N-gram is an array of labels; the labels
	need to match the file's labels exactly.
	"""

	header, data = xwaves_mark.read(fname)
	data = xwaves_mark.mark_to_lab(data, datatype)
	return find(ngram, data)


def find_lab(ngram, fname, loose=0):
	"""ngram = list of labels.
	fname = file name for xwaves_lab datafile.
	
	This function returns all instances
	(even overlapping instances) of the specified
	N-gram in the file.  The return format
	is [ (end_time, label), ... ],
	where the zeroth entry in the list is the
	symbol before the start of the N-gram.
	It's end time is the beginning of the N-gram.

	In the argument list, the N-gram is an array of labels; the labels
	need to match the file's labels exactly.
	"""

	header, data = xwaves_lab.read(fname, loose)
	return find(ngram, data)



def find(ngram, data):
	"""ngram = list of labels.
	data = list of (time, label, ...) as produced by xwaves_lab.py or similar.
	
	This function returns all instances
	(even overlapping instances) of the specified
	N-gram in the file.  The return format
	is [ [ label, ...], ... ] .
	It is a list of n-grams, and each n-gram is a list of entities,
	and each entities is a tuple which marks when it ends,
	what it is specifically, and perhaps other things.

	In the argument list, the N-gram is an array of labels; the labels
	need to match the file's labels exactly.
	"""
	o = []

	ll = [lbl for (t, lbl) in data ]
	N = len(ngram)
	for i in range(1, max(1, len(data)-N+1)):
		if matches(ll[i:i+N], ngram):
			o.append(data[i-1:i+N])
	return o
