"""This module defines closures.
Closures are functions that have been supplied with some arguments,
but not all of them.
"""



class NotYet:
	"""Just a marker, indicating that a certain argument is not yet
	present, and the actual call should be deferred until later.
	"""

	def __repr__(self):
		return "<BLANK>"


class ArgUnspecifiedError(TypeError):
	def __init__(self, s):
		TypeError.__init__(self, s)



class Closure:
	def __init__(self, fcn, *argv, **kwarg):
		"""Create a closure by memorizing a function and its
		arguments.    If all arguments are supplied, you
		can get the result by calling the closure without arguments.
		Missing arguments are replaced by instances of class NotYet;
		such arguments will need to be supplied when the closure is
		called.

		As an additional feature, you can supply a list of users
		of the function's value.    When the value is (eventually)
		produced, the user function(s) will be called with the
		closure's return value.    Users must be functions of one
		argument.
		"""
		self.fcn = fcn
		self.args = argv
		self.argd = kwarg
		self.deferred = []
		self.to_be_filled = []
		for (i, arg) in enumerate(argv):
			if arg is NotYet:
				self.to_be_filled.append(i)

	def __repr__(self):
		return '%s(%s)' % (str(self.fcn),
					','.join([str(q) for q in self.args]
						 + ["%s=%s" % kv for kv in self.argd.items()])
					)

	def __call__(self, *argv, **argd):
		"""This evaluates the closure to either produce a value
		or raise an exception.
		"""
		lstbf = len(self.to_be_filled)
		if len(argv) < lstbf:
			raise ArgUnspecifiedError, len(argv)
		a = list(self.args)
		for (tmparg,j) in zip(argv, self.to_be_filled):
			a[j] = tmparg
		a.extend( argv[lstbf:] )
		adict = self.argd.copy()
		adict.update(argd)
		rv = self.fcn(*a, **adict)
		for user in self.deferred:
			user(rv)
		return rv

	def partial(self, *argv, **argd):
		"""This evaluates the closure to produce another
		(more complete) closure.    Users are not preserved.
		"""
		a = list(self.args)
		for (tmparg,j) in zip(argv, self.to_be_filled):
			a[j] = tmparg
		lstbf = len(self.to_be_filled)
		a.extend( argv[lstbf:] )
		adict = self.argd.copy()
		adict.update(argd)
		rv = Closure(self.fcn, *a, **adict)
		return rv

	def defer(self, user):
		"""This will call the specified function when the closure
		is completed.   It's a bit of a kluge.
		"""
		self.deferred.append( user )




if __name__ == '__main__':
	def foo(a, b):
		return a+b

	x = Closure(foo)
	assert x(1, 3)==4

	x = Closure(foo, 3)
	assert x(4)==7

	try:
		x(1, 1)
	except TypeError:
		pass
	else:
		print "Whoops! Expected TypeError"
	
	try:
		x()
	except TypeError:
		pass
	else:
		print "Whoops! Expected TypeError"

	assert x(b=7)==10

	try:
		x(a=7)
	except TypeError:
		pass
	else:
		print "Whoops! Expected TypeError"
	

	def bar(a, b=8):
		return a*b
	
	y = Closure(bar)
	assert y(a=1)==8
	assert y(a=1,b=2)==2

	y = Closure(bar, 3, 3)
	assert y()==9

	y = Closure(bar, NotYet, 7)

	try:
		y()
	except TypeError:
		pass
	else:
		print "Whoops! Expected TypeError"
	
	assert y(7)==49
	z = y.partial()
	assert z(7)==49
	z = y.partial(8)
	assert z()==56
	def user1(x):
		raise RuntimeError, str(x)
	z.defer(user1)
	try:
		z()
	except RuntimeError, x:
		assert str(x) == "56"
		pass
