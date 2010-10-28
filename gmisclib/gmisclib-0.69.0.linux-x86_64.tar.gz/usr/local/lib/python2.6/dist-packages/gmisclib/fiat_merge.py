#!/usr/bin/env python

import die
import fiatio
import g2_select
import dictops

DEBUG = 0

def merge(d1, d2, key1, key2, grab, unique=True):
	m1 = {}
	d = DEBUG
	for datum1 in d1:
		k = tuple( [datum1[t] for t in key1] )
		if d > 0:
			die.info('Sample datum key1: %s' % str(k) )
			d -= 1
		if unique and k in m1:
			raise ValueError, "Key=%s seen multiple times in d1" % str(k)
		dictops.add_dol(m1, k, datum1)
	m2 = {}
	d = DEBUG
	for datum2 in d2:
		k = tuple( [datum2[t] for t in key2] )
		if d > 0:
			die.info('Sample datum key2: %s' % str(k) )
			d -= 1
		if unique and k in m2:
			raise ValueError, "Key=%s seen multiple times in d2" % str(k)
		dictops.add_dol(m2, k, datum2)


	o = []
	for k in m1.keys():
		if k in m2:
			for a in m1[k]:
				for b in m2[k]:
					tmp = a.copy()
					for (g_from, g_to) in grab:
						tmp[g_to] = g2_select.evaluate(g_from, b)
					o.append( tmp )
	return o



if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	key = []
	unique = True
	grab = []
	while arglist and arglist[0].startswith('-'):
		arg = arglist.pop(0)
		if arg == '--':
			break
		elif arg == '-key':
			key1 = arglist.pop(0).split(',')
			key2 = key1
		elif arg == '-key1':
			key1 = arglist.pop(0).split(',')
		elif arg == '-key2':
			key2 = arglist.pop(0).split(',')
		elif arg == '-grab':
			gcode = arglist.pop(0)
			gout = arglist.pop(0)
			grab.append( (gcode, gout) )
		elif arg == '-D':
			DEBUG += 1
		elif arg == '-multi':
			unique = False
		else:
			die.die('Unknown flag: %s' % arg)
	h1, d1, c1 = fiatio.read(open(arglist.pop(0), 'r'))
	h2, d2, c2 = fiatio.read(open(arglist.pop(0), 'r'))
	assert len(arglist) == 0
	h2.update(h1)
	o = merge(d1, d2, key1, key2, grab, unique)
	fiatio.write(sys.stdout, o, c1 + c2, h2)
