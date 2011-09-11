# -*- coding:utf-8 -*-
from __future__ import print_function
import sys

try:
	import absolute32 as a
except ImportError:
	sys.path.append('../')
	import absolute32 as a

if sys.version < '3':
	exec("chinese = unicode('赖勇浩', 'utf-8')")
else:
	exec("chinese = '赖勇浩'")

assert a.hash('copyright') == -174803930

assert a.hash(chinese) == -1178905243

assert a.hash('Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56)') == 2085310411

##########################################################

assert a.add(1, 1) == 2

assert a.add(0xFFFFFFFF, 2) == 1

assert a.add(0x7FFFFFFF, 2) == -0x7FFFFFFF

##########################################################

assert a.crc(b'copyright') == 947983859

# bytes only
assert a.crc(chinese.encode('utf-8')) == 504349707

assert a.crc(b'Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56)') == -936057631


##########################################################

assert a.adler(b'copyright') == 322503642

# bytes only
assert a.adler(chinese.encode('utf-8')) == 552142447

assert a.adler(b'Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56)') == 764742448

assert a.adler(b'Python 2.6.5 (r265:79063, Apr 16 2010, 13:09:56)' * 3) == -745987698

print('*' * 30)
print('all passed.')

