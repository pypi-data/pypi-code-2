#!/usr/bin/env python
# -*- coding: UTF8 -*-

from reblok import opcodes

HANDLERS = {
}

def dispatch(instr):
	global HANDLERS

	handler = HANDLERS.get(instr, 'do_CLONE')
	return(eval(handler)(instr))

def do_CLONE(instr):
	if not hasattr(instr, '__iter__'):
		return instr

	out = [instr[0]]

	for i in xrange(1, len(instr)):
		out.append(dispatch(instr[i]))

	return out





def raw_SELECT(target):
	"""
		SELECT (fields), (datasources), condition, slice
	"""
	return ['select', (), (target,), None, None]

def merge_SELECT_condition(query, pycond):
	sqlcond = dispatch(pycond)
	print "ZZ", sqlcond

	if query[3] is None:
		query[3] = sqlcond
	else:
		query[3] = (opcodes.AND, query[3], sqlcond)

	return query

def merge_SELECT_slice(query, _slice):
	query[4] = _slice
	return query
