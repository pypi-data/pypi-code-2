#!/usr/bin/env python
import commands,sys,re,math
import decimal
import os

def wc(fname):
    if os.path.exists(fname)==False: return 0;
    f=open(fname)
    counter=0
    for z in f:
        counter=counter+1
    f.close()
    return counter;

def extract_na(fname):
    na_get = re.compile('NA\d+',re.IGNORECASE)
    na_match = na_get.search(fname)
    if na_match:
        return na_match.group().upper()
    else:
        return 0

def mean(x):
    return sum(x) / float(len(x))

def variance(x):
    m_x = mean(x)
    length = len(x)
    if length == 1:
        return decimal.Decimal('NaN')
    sum = 0.
    for k in range(length):
        sum += (x[k]-m_x)**2
    return sum / float(length - 1)

def stdev(x):
    return math.sqrt(variance(x))

########################
# Simple function to intersect two iterables (lists, tuples, etc.)
# http://www.java2s.com/Code/Python/List/Functiontointersecttwolists.htm

# x = intersect([1, 2, 3], (1, 4))    # mixed types
# print x                             # saved result object

def intersect(seq1, seq2):
    res = []                     # start empty
    for x in seq1:               # scan seq1
        if x in seq2:            # common item?
            res.append(x)        # add to end
    return res

########################
# Does pretty much what you'd expect
# >>> x=[1,1,3,3,3,3,5,2]
# >>> unique(x)
# [1, 3, 5, 2]

def unique(x):
    y = []
    for e in x:
        if e not in y:
            y.append(e)
    return y

########################
# Does pretty much what you'd expect
# >>> x=[1,1,3,3,3,3,5,2]
# >>> indices(x,1)
# [0,1]

def indices(x,e):
    y = []
    for k in range(len(x)):
        if x[k] == e:
            y.append(k)
    return y

########################
# This function is a way to get arbitrary elements from a list
# >>> x=[1,1,3,3,3,3,5,2]
# >>> arbslice(x,[0,6,2])
# [1, 5, 3]

def arbslice(x,indices):
    y = []
    for e in indices:
        y.append(x[e])
    return y

########################

######################
# Like arbslice, but gives you back the elements that aren't in the index passed in.

def arbNegSlice(x, indices):
    y = []
    remaining=set(range(0,len(x)))
    remaining=remaining.difference(indices)
    lstRemaining=[z for z in remaining]
    lstRemaining.sort()
    for e in lstRemaining:
        y.append(x[e])
    return y

# numsort.py
# sorting in numeric order
# for example:
#   ['aaa35', 'aaa6', 'aaa261']
# is sorted into:
#   ['aaa6', 'aaa35', 'aaa261']
# Take from: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/135435

def sorted_copy(alist):
    # inspired by Alex Martelli
    # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52234
    indices = map(_generate_index, alist)
    decorated = zip(indices, alist)
    decorated.sort()
    return [ item for index, item in decorated ]

def _generate_index(str):
    """
    Splits a string into alpha and numeric elements, which
    is used as an index for sorting
    """
    #
    # the index is built progressively
    # using the _append function
    #
    index = []
    def _append(fragment, alist=index):
        if fragment.isdigit(): fragment = int(fragment)
        alist.append(fragment)
        
    # initialize loop
    prev_isdigit = str[0].isdigit()
    current_fragment = ''
    # group a string into digit and non-digit parts

    for char in str:
        curr_isdigit = char.isdigit()
        if curr_isdigit == prev_isdigit:
            current_fragment += char
        else:
            _append(current_fragment)
            current_fragment = char
            prev_isdigit = curr_isdigit
    _append(current_fragment)
    return tuple(index)
