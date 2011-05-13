"""This module has functions that help you dynamically import modules.
"""



import sys
import imp
import os.path
from gmisclib import die

def split_name(name):
	"""Split a name in the form    a/b.c into a, b, c, where
	a is a search path,
	b is a module (package) name, and
	c is a name in the module.
	"""
	p = None
	fcn = []
	if '/' in name:
		p, name = os.path.split(name)
	if '.' in name:
		a = name.split('.')
		name = a[0]
		fcn = a[1:]
	return (p, name, fcn)


def load(name, path):
	"""Load a module from the specified list of paths.
	It returns the module, but does not import it.
	If path is None, only look in sys.path and builtins.
	If path is an array containing None, replace the None with sys.path.
	"""
	if path is None:
		pth = None
	else:
		pth = []
		for d in path:
			if d is None:
				pth.extend(sys.path)
			else:
				pth.append( d )
	fd = None
	imp.acquire_lock()
	try:
		fd, pn, desc = imp.find_module(name, pth)
	except ImportError:
		try:
			fd, pn, desc = imp.find_module(name, None)
		except:
			die.warn('#ImportError in load of "%s" from path=%s' % (name, pth))
			imp.release_lock()
			raise

	# If the same module has already been imported, use the existing version.
	if(name in sys.modules and
		hasattr(sys.modules[name], '__file__') and
		os.path.dirname(sys.modules[name].__file__) == os.path.dirname(pn)
			):
		fd.close()
		tmp = sys.modules[name]
		imp.release_lock()
		return tmp

	# print 'name', name, fd, pn, desc
	try:
		pymod = imp.load_module(name, fd, pn, desc)
	finally:
		if fd:
			fd.close()
		imp.release_lock()
	return pymod


load_mod = load
load_inc_path = load
load_mod_inc_path = load_inc_path

_ModuleType = type(sys)

def load_named(name, use_sys_path=True):
	"""Load a module.
	If the module name is in the form a/b,
	it looks in directory "a" first.
	If use_sys_path is true, it searches the entire Python path
	
	It returns the module, but does not import it.
	This version handles importing packages and functions nicely,
	but with less control over the search path.
	
	Usage:
		- load_named_module('/dir/my_module'), or
		- load_named_module('foo/my_module'), or
		- load_named_module('foo/my_module.submodule.function'), or
		- various combinations.
	"""
	p, lname, attrlist = split_name(name)
	# print '#', name, '->', lname
	if use_sys_path:
		path = list(sys.path)
	else:
		path = []
	if p is not None:
		path.insert(0, p)
	try:
		tmp0 = load(lname, path)
	except ImportError, x:
		raise ImportError, "%s in directory '%s'%s" % (str(x), p, ['', ' or sys.path'][use_sys_path])


	tmp = tmp0
	pname = [lname]
	for a in attrlist:
		try:
			tmp = getattr(tmp, a)
		except AttributeError:
			if isinstance(tmp, _ModuleType) and hasattr(tmp, '__path__'):
				try:
					tmp = load(a, tmp.__path__)
				except ImportError, x:
					raise ImportError, "Cannot import %s from package %s at %s (%s)" % (a, '.'.join(pname), tmp.__path__, x)
				pname.append(a)
				continue
			filename = getattr(tmp0, '__file__', None)
			if filename is None:
				filename = getattr(tmp0, '__name__', '???')
			die.info("load_named lookup fails: %s amidst %s" % (a, dir(tmp)))
			raise ImportError, "Cannot look up %s from %s at %s: attempting %s" % (a, '.'.join(pname), tmp0.__path__, '.'.join(attrlist))
		else:
			pname.append(a)
	return tmp


load_named_module = load_named
load_named_fcn = load_named
load_fcn = load_named

def _test():
	assert abs(load_named('math.pi') - 3.14159) < 0.001
	assert load_named('load_mod.load_named.__doc__') == load_named.__doc__
	f = os.path.splitext(die.__file__)[0]
	assert load_named('%s' % f).__doc__ == die.__doc__

if __name__ == '__main__':
	_test()
