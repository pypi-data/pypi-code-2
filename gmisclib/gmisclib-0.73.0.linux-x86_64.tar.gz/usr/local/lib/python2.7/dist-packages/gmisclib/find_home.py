"""This lets you find files with just a path name relative to where
the program's executable code script sits."""

import sys

_scriptname = sys.argv[0]	# Possibly, this is wrong, if we are importing
				# late in execution, after some other module
				# has fiddled with sys.argv.
				# If so, sorry!

import os

__version__ = "$Revision: 1.6 $"


def _searchdir(pathlist, s, access):
	for t in pathlist:
		if t == '':
			t = '.'
		tmp = '%s/%s' % (t, s)
		if os.access(tmp, access) and os.path.isdir(tmp):
			return tmp
	raise RuntimeError, "Can't find %s" % s


def _search(pathlist, s, access):
	for t in pathlist:
		if t == '':
			t = '.'
		tmp = '%s/%s' % (t, s)
		if os.access(tmp, access):
			return tmp
	raise RuntimeError, "Can't find %s" % s


def executable(s, general=True):
	"""Find an executable program.
	It searches first in the directory of the currently executing
	python script.  Optionally, it then looks at PATH.
	If general=False, the function should fail unless
	the executable is in the same directory as the currently
	executing python script."""
	p = [ os.path.dirname( _scriptname ) ]

	if general:
		p.extend( os.environ['PATH'].split(':') )

	return _search(p, s, os.X_OK)



def module(s, general=True):
	"""Find a module. Returns pathname."""
	p = [ os.path.dirname( _scriptname ) ]

	if general:
		p.extend( sys.path )

	return _search(p, "%s.py" % s, os.R_OK)


def os_prgm(nm, general=1):
	"""Find an operating-system dependent executable program."""
	return executable('bin__' + os.uname()[0] + '/' + nm, general)



def data(s):
	"""Find a data file."""
	p = [ '.', os.path.dirname( _scriptname ) ]
	return _search(p, s, os.R_OK)



def directory(s):
	"""Find a directory."""
	p = [ os.path.dirname( _scriptname ) ]
	return _searchdir(p, s, os.X_OK)




if __name__ == '__main__':
	assert data("find_home.py")
