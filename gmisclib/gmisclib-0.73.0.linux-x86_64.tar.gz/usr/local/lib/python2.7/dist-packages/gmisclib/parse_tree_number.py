import sets
import math
import operator as OP

"""This module lets you write mathematical expressions and
build a parse tree.   You can include variables and floats in
the expressions, along with elements of arrays.

You can then walk the parse tree and find out which variables
are used, or which elements of a specified array.
"""

class Array(object):
	def __init__(self, name):
		"""This creates an array.   Arrays are basic
		elements of expressions."""
		self.name = name
	
	def __getitem__(self, key):
		return elementof(self, key)

	def __str__(self, env={}):
		if self.name in env:
			return env[self.name].__str__(env)
		return self.name

	__repr__ = __str__

	def indices(self, env={}):
		raise RuntimeError, 'It is an array'

	def eval(self, env={}):
		raise RuntimeError, 'It is an array'


	def variables(self, env={}):
		if self.name in env:
			return env[self.name].variables(env)
		return sets.Set( ( self.name,) )
	
	def debug(self):
		return '<Array %s>' % self.name

	def _complexity(self):
		return 2


class output_mixin(object):
	def __init__(self):
		pass

	def eval(self, env={}):
		"""This returns an Expression.
		"""
		raise RuntimeError, 'Virtual!'

	def variables(self, env={}):
		"""Any definitions in env are used to resolve otherwise
		undefined names.    This returns a Set containing
		all undefined variable names.
		"""
		raise RuntimeError, 'Virtual!'

	def indices(self, variable, env={}):
		raise RuntimeError, 'Virtual!'

	def debug(self):
		return '<Output_mixin: virtual!>'

	def __str__(self, env={}):
		"""Env is optional. Anything defined in env is used
		to resolve references, but the outcome may still contain
		undefined variables, which are printed as names.
		"""
		raise RuntimeError, 'Virtual!'

	def _complexity(self):
		raise RuntimeError, "Virtual!"


def _is_opNg1(x, op):
	assert op in _operator.Priority
	return isinstance(x, operatorNg1) and x.op==op

def _is_op1(x, op):
	assert op in _operator.Priority
	return isinstance(x, operator1) and x.op==op

def _IMO_float(a, b, indent):
	if a is b:
		return Float(1.0)
	try:
		fb = float(b)
	except TypeError:
		pass
	else:
		# b is a Float
		if fb == 0.0:
			return None
		# b is a nonzero float
		try:
			fa = float(a)
		except TypeError:
			# a is an expression
			# This is the degenerate case expression/float, which is useless
			# and leads to infinite loops.
			return None
		else:
			# Both a and b are floats.
			return Float(fa/fb)
	return None


def _IMO_Name(a, b, indent):
	if isinstance(a, Name) and isinstance(b, Name) and a.name==b.name:
		return Float(1.0)
	return None

def _IMO_elementof(a, b, indent):
	if isinstance(a, elementof) and isinstance(b, elementof):
		# Need to think about the following test a bit...
		# print indent+'is_mul_of element element', a.array, a.index, b.array, b.index
		if str(a.array)==str(b.array) and str(a.index)==str(b.index):
			return Float(1.0)
	return None


def _IMO_products(a, b, indent):
	if _is_opNg1(a, '*'):
		atmp = list(a.operands)
	else:
		atmp = [ a ]
	if _is_opNg1(b, '*'):
		btmp = list(b.operands)
	else:
		btmp = [ b ]
	# print 'atmp=', atmp
	# print 'btmp=', btmp
	if len(atmp) + len(btmp) > 2:
		rtmp = []
		while atmp:
			ai = atmp.pop()
			t = None
			for j in range(len(btmp)):
				# print indent+'Checking is_mul_of', ai, btmp[j]
				t = is_mul_of(ai, btmp[j], indent+'#')
				if t is not None:
					tmp = coerce_into(t)
					if tmp._complexity() < ai._complexity()+btmp[j]._complexity():
						break
			if t is not None:
				# print 'Cancellation', j, ai, btmp[j], '->', t
				atmp.append(t)
				btmp.pop(j)
			else:
				rtmp.append( ai )
		if len(btmp) == 0:
			rv = rtmp[0]
			for rt in rtmp[1:]:
				rv *= rt
			return rv
		# print indent+'IMO: leftovers:', rtmp, atmp, btmp
	return None


def _IMO_neg(a, b, indent):
	if _is_op1(a, 'U-') and _is_op1(b, 'U-'):
		return is_mul_of(a.operand, b.operand, indent+'#')
	if _is_op1(a, 'U-'):
		t = is_mul_of(a.operand, b, indent+'#')
		if t is not None:
			return -t
	if _is_op1(b, 'U-'):
		t = is_mul_of(a, b.operand, indent+'#')
		if t is not None:
			return -t
	return None


def _IMO_exp(a, b, indent):
	if _is_op1(a, 'exp') and _is_op1(b, 'exp'):
		return operator1('exp', a.operand-b.operand)
	return None


def _IMO_pow(a, b, indent):
	if _is_opNg1(a, '**') and len(a.operands)==2:
		if a.operands[1] >= 1.0:
			t = is_mul_of(a.operands[0], b, indent+'#')
			# (tx)^n / x = t^n x^(n-1)
			if t is not None:
				return operatorN('*', operatorN('**', [ t, a.operands[1] ] ),
							operatorN('**', [ b, operatorN('-', a.operands[1], 1) ] )
						)
	if _is_opNg1(a, '**') and len(a.operands)==2 and _is_opNg1(b, '**') and len(b.operands)==2:
		if a.operands[1] >= b.operands[1]:
			t = is_mul_of(a.operands[0], b.operands[0], indent+'#')
			# (tx)^n / x^m = t^n x^(n-m)
			if t is not None:
				return operatorN('*', operatorN('**', t, a.operands[1]),
							operatorN('**', b,
									operatorN('-', [ a.operands[1],
											b.operands[1] ]
										)
								)
						)
	return None


def is_mul_of(a, b, indent=''):
	"""Returns the ratio a/b if a contains b as a factor,
	returns None otherwise.
	The routine does not promise to find all possible factors.
	"""
	# print indent+'PTN.is_mul_of', a, b
	for test in [
			# _IMO_float,
			_IMO_Name, _IMO_elementof,
			_IMO_neg,
			_IMO_products,
			_IMO_exp, _IMO_pow
			]:
		tmp = test(a, b, indent)
		if tmp is not None:
			# print "IMO: a=", a, 'b=', b
			# print 'type(tmp)=', type(tmp), 'test=', tmp
			if tmp._complexity() < a._complexity()+b._complexity():
				return tmp
	return None





class abstract_number(object):
	def __init__(self):
		pass

	def __add__(self, other):
		# print '__add__', str(self), str(other)
		try:
			fs = float(self)
		except TypeError:
			fs = None
		try:
			fo = float(other)
		except TypeError:
			fo = None
		if fo is not None and fs is not None:
			return Float(fo + fs)
		if fs == 0.0:
			return other
		if fo == 0.0:
			return self

		other = coerce_into(other)

		if _is_opNg1(self, '+'):
			a = list(self.operands)
		else:
			a = [ self ]
		if _is_opNg1(other, '+'):
			b = list( other.operands )
		else:
			b = [ other ]

		# print '__add__ a=', a
		# print '__add__ b=', b
		ao = []
		while a:
			ai = a.pop()
			# print 'A.pop =', ai
			for j in range(len(b)):
				# print '__add__IMO ab', j, ai, b[j]
				t1 = is_mul_of(ai, b[j])
				if t1 is not None:
					tmp = coerce_into(t1+1.0)*b[j]
					# print 'tmp=', tmp
					if tmp._complexity() < ai._complexity()+b[j]._complexity()+1:
						a.append(tmp)
						# print 'a.append',  tmp
						b.pop(j)
						ai = None
						break
					else:
						# print "\ttoo complex:", tmp, tmp._complexity(), ai._complexity(), b[j]._complexity()
						pass
				# print '__add__IMO ba', j, b[j], ai
				t2 = is_mul_of(b[j], ai)
				if t2 is not None:
					tmp = coerce_into(t2+1.0)*ai
					# print 'tmp=', tmp
					if tmp._complexity() < ai._complexity()+b[j]._complexity()+1:
						a.append(tmp)
						ai = None
						# print 'a.append', tmp
						b.pop(j)
						break
					else:
						# print "\t too complex:", tmp, tmp._complexity(), ai._complexity(), b[j]._complexity()
						pass
			if ai:
				ao.append(ai)
		# print '__add__ ao =', ao
		# print '__add__ btuple=', b
		return operatorN('+', tuple(ao) + tuple(b))

	__radd__ = __add__
	
	def __sub__(self, other):
		try:
			fs = float(self)
		except TypeError:
			fs = None
		try:
			fo = float(other)
		except TypeError:
			fo = None
		if fo is not None and fs is not None:
			return Float(fs - fo)
		if fs == 0.0:
			return operator1('U-', other)
		if fo == 0.0:
			return self
		other = coerce_into(other)
		if _is_op1(other, 'U-'):
			return operatorN('+', (self, other))
		if _is_op1(self, 'U-'):
			return operator1('U-', operatorN('+', (self, other)))
		return operatorN('-', (self, other))

	def __rsub__(self, other):
		return other.__sub__(self)

	def __pow__(self, other):
		try:
			fs = float(self)
		except TypeError:
			fs = None
		try:
			fo = float(other)
		except TypeError:
			fo = None
		if fo is not None and fs is not None:
			return Float(fs ** fo)
		other = coerce_into(other)
		if _is_float(self, 1.0):
			return Float(1.0)
		if _is_float(other, 1.0):
			return self
		if _is_float(other, 0.5):
			return operator1('sqrt', self)
		return operatorN('**', (self, other))

	def __rpow__(self, other):
		return other.__pow__(self)

	def __mul__(self, other):
		# print 'PTN __mul__', str(self), str(other)
		try:
			fs = float(self)
		except TypeError:
			fs = None
		try:
			fo = float(other)
		except TypeError:
			fo = None
		if fo is not None and fs is not None:
			return Float(fo * fs)
		if fs == 1.0:
			return other
		if fo == 1.0:
			return self
		if fs == -1.0:
			return operator1('U-', other)
		if fo == -1.0:
			return operator1('U-', self)

		other = coerce_into(other)

		if _is_op1(self, 'U-') and _is_op1(other, 'U-'):
			self = self.operand
			other = other.operand

		if _is_opNg1(self, '*'):
			if _is_opNg1(other, '*'):
				# print '\tmore', other.operands
				return self.more(other.operands)
			else:
				# print '\tMore', str(other)
				return self.more( (other,) )
		# print 'PTN_mul_out', self, other
		return operatorN('*', (self, other))

	__rmul__ = __mul__

	def __div__(self, other):
		# print '__div__', self, other
		try:
			fs = float(self)
		except TypeError:
			fs = None
		try:
			fo = float(other)
		except TypeError:
			fo = None
		if fo is not None and fs is not None:
			return Float(fs / fo)
		if fo == 1.0:
			return self
		if fo == -1.0:
			return operator1('U-', self)
		if fo is not None and _is_opNg1(self, '*'):
			modified = False
			atmp = list(self.operands)
			for (i, op) in enumerate(atmp):
				try:
					f = float(op)
				except TypeError:
					pass
				else:
					atmp[i] = Float(f/fo)
					modified = True
			if modified:
				rv = atmp[0]
				for rt in atmp[1:]:
					rv *= rt
				return rv

		other = coerce_into(other)

		t = is_mul_of(self, other)
		if t is not None:
			tmp = coerce_into(t)
			if tmp._complexity() < self._complexity + other._complexity():
				return tmp

		if _is_op1(self, 'U-') and _is_op1(other, 'U-'):
			self = self.operand

		return operatorN('/', (self, other))

	def __rdiv__(self, other):
		return other.__div__(self)
	
	__truediv__ = __div__
	__rtruediv__ = __rdiv__

	def __neg__(self):
		try:
			fs = float(self)
		except TypeError:
			pass
		else:
			return Float(-fs)

		if _is_op1(self, 'U-'):
			# -(-x) = x
			return self.operand
		if _is_opNg1(self, '-') and len(self.operands)==2:
			return operatorN('-', (self.operands[1], self.operands[0]))
		return operator1('U-', self)

	def __pos__(self):
		return self
	
	def __abs__(self):
		if _is_op1(self, 'U-'):
			return operator1('abs', self.operand)
		if _is_op1(self, 'exp') or _is_op1(self, 'abs'):
			return self
		return operator1('abs', self)



_Opfcn = {'-': OP.neg, 'abs': abs,
	'sin': math.sin, 'cos': math.cos, 'exp': math.exp,
	'log': math.log
	}
def _do_math(x, name):
	try:
		f = float(x)
	except TypeError:
		# print 'Name=', name
		return operator1(name, x)
	else:
		return _Opfcn[name](f)


def abs(x):
	if _is_op1(x, 'abs'):	# abs(abs(x)) = x
		return x
	_do_math(x, 'abs')

def cos(x):
	if _is_op1(x, 'abs'):	# cos(abs(x)) = cos(x)
		return _do_math(x.operand, 'cos')
	return _do_math(x, 'cos')

def sin(x):
	return _do_math(x, 'sin')

def exp(x):
	return _do_math(x, 'exp')


def log(x):
	if _is_op1(x, 'exp'):	# log(exp(x)) = x
		return x
	return _do_math(x, 'log')


def sqrt(x):
	if _is_opNg1(x, '**') and len(x.operands)==2 and _is_float(x.operands[1], 2.0):
		# sqrt(x**2) = abs(x)
		return operator1('abs', x.operands[0])
	return _do_math(x, 'sqrt')


class Expression(abstract_number,output_mixin):
	def __init__(self, value):
		abstract_number.__init__(self)
		output_mixin.__init__(self)
		self.x = coerce_into(value)
		self._check()
	
	def _check(self):
		assert isinstance(self.x, Float) or isinstance(self.x, abstract_number), 'Bad type=%s' % str(type(self.x))

	def __iadd__(self, other):
		self._check()
		ci = coerce_into(other)
		# print 'PTN __iadd', type(self.x), self.x.debug(), type(ci), ci.debug()
		self.x = self.x + ci
		# print 'PTNa __iadd', type(self.x), self.x.debug()
		self._check()
		return self

	def __isub__(self, other):
		self._check()
		self.x = self.x - coerce_into(other)
		self._check()
		return self

	def __imul__(self, other):
		self._check()
		self.x = self.x * coerce_into(other)
		self._check()
		return self

	def __idiv__(self, other):
		self._check()
		self.x = self.x / coerce_into(other)
		self._check()
		return self

	def eval(self, env={}):
		return self.x.eval(env)

	def variables(self, env={}):
		return self.x.variables(env)
	
	def indices(self, variable, env={}):
		return self.x.indices(variable, env)

	def __str__(self, env={}):
		# print 'self.x=', self.x, self.x.debug()
		return self.x.__str__(env)

	__repr__ = __str__

	def debug(self):
		return 'E%s' % self.x.debug()

	def __float__(self):
		# print 'PTN float(expression)', self.x
		return float(self.x)
	
	def priority(self):
		return self.x.priority()

	def _complexity(self):
		return self.x.complexity()

class Name(abstract_number,output_mixin):
	def __init__(self, name):
		"""This creates a named variable.   Names are
		basic parts of expressions."""
		abstract_number.__init__(self)
		output_mixin.__init__(self)
		self.name = name

	def __str__(self, env={}):
		if self.name in env:
			return str(env[self.name])
		return self.name

	__repr__ = __str__

	def eval(self, env):
		return env.get(self.name, self.name)

	def variables(self, env={}):
		if self.name in env:
			return env[self.name].variables(env)
		else:
			return sets.Set( ( self.name,) )

	def indices(self, variable, env={}):
		if self.name in env:
			return env[self.name].indices(variable, env)
		else:
			return sets.Set()

	def debug(self):
		return '<Name %s>' % self.name

	def _complexity(self):
		return 2


class Float(abstract_number,output_mixin):
	def __init__(self, v):
		self.v = float(v)

	def eval(self, env={}):
		return self.v

	def variables(self, env={}):
		return sets.Set()
	
	def indices(self, variable, env={}):
		return sets.Set()

	def debug(self, env={}):
		return '<Float %g>' % self.v
	
	def __str__(self, env={}):
		return str(self.v)
	
	def __float__(self):
		# print 'Float -> float', self.v
		return self.v

	def _complexity(self):
		return 1


def _is_float(x, v):
	# print 'PTN, _is_float, type', type(x), x, str(x)
	try:
		f = float(x)
	except TypeError:
		return None
	return f == v


class _operator(abstract_number, output_mixin):
	Priority = {'U-': 5, 'abs': 5, 'sin':5, 'cos':5, 'exp':5,
			'sqrt':5, 'log': 5,
			'+': 2, '-': 2, '*': 3, '/': 3,
			'**': 4,
			'[]': 6
			}

	def __init__(self, operator):
		abstract_number.__init__(self)
		output_mixin.__init__(self)
		self.op = operator

	def priority(self):
		return self.Priority[self.op]


def coerce_into(x):
	if isinstance(x, Expression):
		x = x.x

	try:
		f = float(x)
	except TypeError:
		# print 'coerce_type=', type(x)
		assert isinstance(x, abstract_number)
		assert isinstance(x, output_mixin)
		# print 'Type=', str(type(x))
		return x
	else:
		return Float(x)


class operator1(_operator):
	Printable = {'U-': '-', 'abs': 'abs',
			'sin': 'math.sin', 'cos': 'math.cos',
			'exp': 'math.exp', 'log': 'math.log',
			'sqrt': 'math.sqrt'
			}
	def __init__(self, operator, operand):
		# print 'Operator1: operator=', operator
		_operator.__init__(self, operator)
		self.operand = operand
		assert self.op

	def __str__(self, env={}):
		return '%s(%s)' % (self.Printable[self.op], str(self.operand))
	__repr__ = __str__
	
	def eval(self, env={}):
		_do_math( self.op, self.operand.eval(env) )

	def variables(self, env={}):
		return self.operand.variables(env)

	def indices(self, variable, env={}):
		return self.operand.indices(variable, env)

	def debug(self):
		return '<op1:%s %s>' % (self.op, self.operand.debug())

	def _complexity(self):
		return 1 + len(self.operand)


class elementof(_operator):
	def __init__(self, array, index):
		_operator.__init__(self, '[]')
		self.array = array
		self.index = index
	
	def __str__(self, env = {}):
		index = repr(env.get(self.index, self.index))
		array = str(env.get(self.array, self.array))
		return '%s[%s]' % (array, index)
	__repr__ = __str__
	

	def variables(self, env={}):
		tmp = sets.Set()
		tmp.update( self.array.variables(env) )
		try:
			v = self.index.variables(env)
			tmp.update( v )
		except AttributeError:
			pass
		return tmp

	def indices(self, variable, env={}):
		tmp = sets.Set()
		if isinstance(self.array, Array) and self.array.name==variable:
			if isinstance(self.index, abstract_number):
				tmp.add( self.index.eval(env) )
			else:
				tmp.add(self.index)
		return tmp

	def debug(self):
		if isinstance(self.array, Array):
			a = self.array.debug()
		else:
			a = str(self.array)
		if isinstance(self.index, abstract_number):
			i = self.index.debug()
		else:
			i = str(self.index)
		return '%s[%s]' % (a, i)

	# def provably_eq(self, other):
		# return self.array.provably_equal(other.array)


	def _complexity(self):
		if isinstance(self.array, Array):
			a = self.array._complexity()
		else:
			a = 0
		if isinstance(self.index, abstract_number):
			a += self.index._complexity()
		return a



def operatorN(operator, operands):
	if len(operands) == 1:
		return operands[0]
	nf = 0
	for o in operands:
		try:
			float(o)
			nf += 1
		except TypeError:
			pass
	assert nf<len(operands), "All floats!"
	return operatorNg1(operator, operands)


class operatorNg1(_operator):
	def __init__(self, operator, operands):
		_operator.__init__(self, operator)
		assert type(operands) == type( () )
		assert len(operands) > 1
		self.operands = operands
	
	def more(self, items):
		assert type(items) == type( () )
		return operatorNg1(self.op, self.operands + items)
	
	def __str__(self, env={}):
		tmp = []
		p = self.priority()
		# print 'OP=', self.op, p
		# print 'self=', self.debug()
		for o in self.operands:
			# print 'o=', o.debug(), 'OPp=', p
			try:
				if o.priority() <= p:
					# print '() pri=', o.priority()
					tmp.append( '(%s)' % o.__str__(env) )
				else:
					# print 'NO()', type(o), o, o.priority()
					tmp.append( o.__str__(env) )
			except AttributeError, x:
				# print 'ATTRERR', x
				so = str(o)
				if so.startswith('-'):
					tmp.append( '(%s)' % so)
				else:
					tmp.append( so )
		return self.op.join( tmp )
	__repr__ = __str__
	
	def variables(self, env={}):
		tmp = sets.Set()
		for o in self.operands:
			tmp.update( o.variables(env) )
		return tmp
	
	def indices(self, variable, env={}):
		tmp = sets.Set()
		for o in self.operands:
			tmp.update( o.indices(variable, env) )
		return tmp
	
	def debug(self):
		dl = [ x.debug() for x in self.operands ]
		if len(dl) > 5:
			dl = dl[:4] + ['...']
		return '<opNg1:%s %s>' % (self.op, ' '.join(dl))


	def _complexity(self):
		c = 1
		for op in self.operands:
			c += op._complexity()
		return c


if __name__ == '__main__':
	x = 3.0
	z = 3.0
	y = Name('q')
	w = x + y + y
	print 'w=', w
	print 'wz*wz*wz=', (w+z)*(w+z)*(w+z)
	print 'w.variables()=', w.variables()
	print 'w*w.variables()=', (w*w).variables()
	print '---------- arrays --'
	a = Array('p')
	print "a['x']=", a['x']
	print (336.0*a[5])/336.0 - (a[5]*336.0)/336.0
	print a[1]+a[3]+a[1]
	print a[1]
	print a[1]+a[1]
	print (a[1]+a[1]+a[1]+a[1])/4
	print a[1]+y+x
	print (a[1]+y+x)/336
	print (a[1]+a[2]+a[3])/336
	print a[1].variables()
	print a[1].indices('p')
	print (a[1]+a[3]+a[Name('q')]).indices('p')
	print a[1].indices('b')
	print '--------Expressions-----'
	q = Expression(0.0)
	print 'Float(Expression)=', float(q)
	q += w
	print q
	print q.variables()
