
"""This module is designed to build makefiles."""

import os
import re
import sys
import tempfile
import datetime
import subprocess

from gmisclib import die
from gmisclib import avio
from gmisclib import fiatio
from gmisclib import gpkmisc

_debug = False
_log = None
makeflags = []
makefile = None
_makefd = None
_makeprog = ['make']
_did_header = False
DB_format = 'fiatio'


def maketemp(dir='/tmp', prefix='maketemp', suffix=''):
	global makefile, _makefd
	gpkmisc.makedirs(dir)
	handle, makefile = tempfile.mkstemp(dir=dir, prefix=prefix, suffix=suffix)
	_makefd = os.fdopen(handle, 'w')


def _write(*s):
	global _makefd
	for x in s:
		_makefd.writelines([x, '\n'])


def _header():
	global _did_header
	if _did_header:
		return
	_write("# Makefile produced by gmisclib/makemake.py")
	_write(".SUFFIXES:", "")
	_write(".PHONY: all", "")
	_did_header = True


def setlog(f):
	global _log
	_log = open(f, 'a')


def log(*s):
	"""Log some strings, one per line."""
	for x in s:
		_log.writelines([x, '\n'])
	_log.flush()



_qp = re.compile('[^a-zA-Z0-9_.+,/:-]')
def quote(s):
	def replf(x):
		return '\\%s' % x
	return re.sub(_qp, replf, s)


def var(k, v):
	"""Pass a variable to make."""
	_header()
	_write('%s = %s' % (k, v))


def rule(a, *b):
	"""Writes a rule into a makefile.   All lines except the
	first are indented.
	"""
	_write('', a)
	_write( *['\t%s' % t for t in b] )
	_write('')


def blank():
	_header()
	_write("")
	

def set_debug():
	global _debug
	_debug = True


def finish():
	global _makefd, makefile, makeflags
	# _makefd.flush()
	# os.fsync(_makefd.fileno())
	_makefd.close()
	if _debug:
		tmp = open(makefile, 'r')
		sys.stdout.writelines(tmp.readlines())
	else:
		args = _makeprog + ['-f', makefile] + makeflags
		print '# calling', args
		rv = subprocess.call(args)
		os.remove(makefile)
		if rv != 0:
			die.info("CALL: %s" % (' '.join(args)))
			die.die("Make fails with %d" % rv)

def date():
	return datetime.datetime.now().ctime()


class FileNotFound(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)



def path_to(s):
	for d in os.environ['PATH'].split(':'):
		tmp = os.path.join(d, s)
		if os.access(tmp, os.X_OK):
			return tmp
	raise FileNotFound, s


def set_make_prog(*s):
	global _makeprog
	try:
		path_to(s[0])
	except FileNotFound:
		die.die("Specified make program '%s' not on PATH" % s[0])
	_makeprog = s


def ncpu():
	"""
	@rtype: str   !Not an integer!
	@return: a string representation of the integer number of cores that
		the computer has.
	"""
	n = 0
	for x in open('/proc/cpuinfo', 'r'):
		if x.split(':')[0].strip() == 'processor':
			n += 1
	assert n > 0, "Silly!"
	return str(n)


def read(fn):
	if DB_format == 'avio':
		h, d, c = avio.read_hdc(open(fn, 'r'))
	elif DB_format == 'fiatio':
		h, d, c = fiatio.read(open(fn, 'r'))
	else:
		die.die("Unknown metadata format: %s" % DB_format)
	return h, d
