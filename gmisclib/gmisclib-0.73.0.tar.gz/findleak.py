# -*- Mode: Python; tab-width: 4 -*-

__author__ = "Samual M. Rushing"
# See http://www.nightmare.com/medusa/memory-leaks.html

import sys
import types
import os
import re

def get_refcounts():
    d = {}
    # collect all classes
    for m in sys.modules.values():
        for sym in dir(m):
            o = getattr (m, sym)
            if type(o) is types.ClassType:
                d[o] = sys.getrefcount (o)
    # sort by refcount
    pairs = [ (x[1], x[0]) for x in d.items() ]
    pairs.sort()
    pairs.reverse()
    return pairs


def print_top_N(N=100, prefix='#TOPref'):
	for (n, c) in get_refcounts()[:N]:
		if n > 8:
			print '%s%10d %s.%s' % (prefix, n, c.__module__, c.__name__)


def readvm():
	fd = open("/proc/%d/status" % os.getpid(), "r")
	lines = fd.readlines()
	fd.close()
	nvms = 0
	for line in lines:
		a = line.split()
		if a[0] == 'VmData:':
			assert a[2] == 'kB'
			nvms = int(a[1])
	return nvms

_a1kid = 1
def alloc1k():
	global _a1kid
	tmp = ('%10d' % _a1kid) * 100
	_a1kid += 1
	return tmp

_vmstat = 0
def vm(comment=''):
	global _vmstat
	nvms = 0
	prefix = '#VMSTAT: '
	size = 0
	tmp1 = readvm()
	memstore = []
	while 1:
		memstore.append( alloc1k() )
		size += 1
		tmp2 = readvm()
		if tmp2 > tmp1:
			break
		# print 'len(ms)', len(memstore), tmp2, tmp1
	nvms = tmp1 + 1 - size
	delta = nvms - _vmstat
	_vmstat = nvms
	print '%s%d # %s' % (prefix, delta, comment)

vm('STARTUP')


def lookvmstat(fname):
	def usage_add(u, id, v):
		try:
			u_id = u[id]
			x = (1 + u_id[0], v+u_id[1])

		except KeyError:
			x = (1, v)
		u[id] = x

	fd = open(fname, 'r')
	vml = re.compile('^#VMSTAT:')
	usage = {}
	while 1:
		l = fd.readline()
		if l == '':
			break
		if vml.match(l):
			a = l.strip().split()
			if a[2] != '#':
				continue
			id = ' '.join(a[3:])
			vec = float(a[1])
			usage_add(usage, id, vec)
	fd.close()
	tmp = [ ( -v[1]/float(v[0]), id, v) for (id, v) in usage.items() ]
	tmp.sort()
	for (fom, id, v) in tmp[:20]:
		print id, v


if __name__ == '__main__':
    vm()
    print_top_N()
    vm()
    print_top_N()
    vm()
    tmp = 'adadsadadasd' * 1000
    vm()
    tmp = None
    vm()


