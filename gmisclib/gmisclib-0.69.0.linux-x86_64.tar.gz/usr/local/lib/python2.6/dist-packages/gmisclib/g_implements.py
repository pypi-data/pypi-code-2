"""This module tells you if an object's signature matches a class.
It lets you know if one class can substitute for another,
even if they are unrelated in an OO hierarchy.

This allows you to begin to check that a foreign object will have the
necessary properties to be used in your code.   It is more of a
functional check than C{isimplements}().

For instance, if your code needs a write() method, you
can check for it like this::

	class some_template(object):
		def write(self, somearg):
			pass
	#
	g_implements.check(x, some_template)
	#... at this point, we can be assured that a
	# call to x.write(3) is possible.
	# (Note that we don't know what the call will *do*,
	# merely that the proper method of x exists and that
	# it can take an argument.

Semi-kluge:   if you have an instance, C{i} that needs to convince
C{g_implements} that it can actually behave as class C{C},
then set C{i.__g_implements__ = ['C']}.
Generally, this can be a list or set of class names.
This trick is useful for C-implementations of python classes
(where introspection cannot get all the necessary information) or
for fancy python classes that use C{__getattribute__} and similar.
"""

import inspect

_cache = {}
# g_implements keeps a cache of previous results for speed.  MAXCACHE
# sets the size of the number if types to remember.  Note that the classes
# are cached, not the instances themselves.   You can call L{why}(o, C)
# with a million different objects C{o}, and as long as all of them are
# in the same class, this will only occupy one cache slot.
# (And, the million queries will be answered from the cache as long as all
# of the C{o} are in the same class.)
MAXCACHE = 100

Optional = 'optional'
Varargs = 'varargs'
def Vartype(mem, com):
	return True
def Strict(mem, com):
	return False

Ignore = set( ['__class__', '__delattr__', '__module__', '__new__',
			'__doc__', '__dict__', '__getattribute__',
			'__hash__',
			'__repr__', '__str__',
			'__reduce__', '__reduce_ex__', '__setattr__',
			'__weakref__', '__slots__'
			]
		)


def why(instance, classobj):
	"""Explains why instance doesn't implement the classobj.
	@param instance: an instance of a class
	@param classobj: a class object
	@return: None (if it does) or a string explanation of why it doesn't
	@rtype None or str
	"""
	try:
		c = instance.__class__
	except AttributeError:
		return "Instance (arg 1) has no __class__ attribute."
	key = (c, classobj)
	try:
		return _cache[key]
	except KeyError:
		pass
	assert MAXCACHE >= 0
	while len(_cache) > MAXCACHE:
		_cache.popitem()

	try:
		# This is a semi-kluge to allow an instance to declare that it
		# can implement a particular class.
		if classobj.__name__ in instance.__g_implements__:
			_cache[key] = None
			return None
	except AttributeError:
		pass

	for mem in dir(classobj):
		if mem in Ignore:
			continue
		v = getattr(classobj, mem)
		gis = getattr(v, 'g_implements', Strict)
		if gis == Optional:
			continue
		if not hasattr(c, mem):
			_cache[key] = 'Missing member: %s; %s does not implement %s' % (mem, str(type(instance)), str(classobj))
			return _cache[key]
		com = getattr(c, mem)
		if callable(gis) and gis(mem, com):
			continue
		if inspect.ismethod(com):
			if inspect.ismethod(v):
				vargs, vv, vk, vdef = inspect.getargspec(v.im_func)
				margs, mv, mk, mdef = inspect.getargspec(com.im_func)
	
				if mdef is None:
					matchlen = len(margs)
				else:
					matchlen = len(margs)-len(mdef)
				if vargs[:matchlen] != margs[:matchlen]:
					if gis == Varargs:
						continue
					_cache[key] = "Method argument list does not match for %s: %s instead of %s; type=%s does not implement %s" \
								% (mem, margs[:matchlen], vargs[:matchlen],
									str(type(instance)), str(classobj))
					return _cache[key]
			elif inspect.ismethoddescriptor(v):
				continue
		elif type(com) != type(v):
			_cache[key] = 'Wrong type for %s: %s instead of %s; type=%s does not implement %s' \
					% (mem, type(com), type(v),
						str(type(instance)), str(classobj)
						)
			return _cache[key]
	_cache[key] = None
	return _cache[key]


def impl(instance, classobj):
	"""Tells you if an instance of an object implements a class.
	By implements, I mean that the instance supplies every member
	that the class supplies, and every member has the same type.
	The instance may have *more* members, of course.
	Functions require that the argument names must match, too
	at least as far as the required arguments in the classobj's function.

	The match may be made looser by adding a g_implements attribute
	to various class members.  Possibilities for the value
	are Optional, Strict, Vartype, Varargs, or you can give
	a two-argument function, and that function will be called
	to decide whether the match is acceptable or not.
	"""
	return why(instance, classobj) is None


def make_optional(x):
	"""This is a decorator for a function.
	make_optional implies make_varargs.
	"""
	x.g_implements = Optional
	return x

def make_varargs(x):
	"""This is a decorator for a function."""
	x.g_implements = Varargs
	return x

def make_vartype(x):
	"""This is a decorator for a function."""
	x.g_implements = Vartype
	return x

def make_strict(x):
	"""This is a decorator for a function."""
	x.g_implements = Strict
	return x


class GITypeError(TypeError):
	"""Exception raised by L{check} to indicate failure.
	"""
	def __init__(self, s):
		TypeError.__init__(self, s)


def check(instance, classobj):
	"""Require that C{instance} has the attributes defined by C{classobj}.
	This function either quietly succeeds or it raises a GITypeError exception.
	@type instance: any instance of a class (i.e. anything with a C{__class__} attribute).
	@type classobj: any class object (i.e. not an instance, typically).
	@param instance: the thing to check
	@param classobj: a class that provides a pattern of attributes.
	@raise GITypeError: C{instance} doesn't provide all the features of C{classobj}.
	"""
	w = why(instance, classobj)
	if w is not None:
		raise GITypeError, w


class _tc1(object):
	x = 1
	y = ''
	def z(self, foo):
		return foo

class _tc2(object):
	def __init__(self):
		pass

class _tc1a(object):
	x = 0
	y = 'x'
	def z(self, foo):
		return foo+1

class _tc3(object):
	x = 0.0
	y = 'x'
	def z(self, foo):
		return foo+1

class _tc1b(object):
	x = 0
	y = 'x'
	def z(self, foo):
		return foo+1
	w = []
	def foo(self, a, b):
		return a+b


class _tc0a(object):
	x = 1

class _tc0b(object):
	y = ''
	def z(self, foo):
		return 0

class _tc1c(_tc0a, _tc0b):
	pass

class _tc2a(object):
	x = 1
	y = ''
	def z(self, bar):
		return bar

def test():
	assert not impl(_tc1(), _tc2)
	check(_tc1(), _tc1a)
	assert not impl(_tc1(), _tc3)
	assert not impl(_tc1(), _tc1b)
	check(_tc1b(), _tc1)
	check(_tc1c(), _tc1)
	check(_tc1(), _tc1c)
	assert not impl(_tc1(), _tc2a)

if __name__ == '__main__':
	test()
