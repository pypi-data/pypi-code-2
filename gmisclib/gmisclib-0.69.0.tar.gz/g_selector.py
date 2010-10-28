import re
import die

"""This selects dictionaries (i.e. sets of attribute=value pairs),
to see if they meet specified criteria.
"""


class selector:
	def accept(self, item):
		return self.x.accept(item)

	def __init__(self):
		self.x = true()

	def and_another(self, txt):
		if isinstance(self.x, true):
			self.x = one_selector(txt)	# Leaf node
		elif isinstance(self.x, false):
			pass
		else:
			self.x = selector_op(self.x, _and, one_selector(txt) )

	select = and_another

	def or_another(self, txt):
		if isinstance(self.x, false):
			self.x = one_selector(txt)	# Leaf node
		elif isinstance(self.x, true):
			pass
		else:
			self.x = selector_op(self.x, _or, one_selector(txt) )
	
	def And(self, s):
		self.x = selector_op(self.x, _and, s)
	
	def Or(self, s):
		self.x = selector_op(self.x, _or, s)

	def Not(self):
		self.x = selector_not(self.x)
	
	def leaf(self, txt):
		self.x = one_selector(txt)

	def filterlist(self, x):
		o = []
		for datum in x:
			if self.accept(datum):
				o.append( datum )
		return o


class true(selector):
	def __init__(self):
		pass
	def accept(self, item):
		return True

class false(selector):
	def __init__(self):
		pass
	def accept(self, item):
		return False


def _and(x, l, r):
	if l.accept(x):
		return r.accept(x)
	return False


def _or(x, l, r):
	if l.accept(x):
		return True
	return r.accept(x)


class selector_op(selector):
	def __init__(self, l, op, r):
		self.l = l
		self.r = r
		self.op = op

	def accept(self, x):
		return (self.op)(x, self.l, self.r)


def selector_not(selector):
	def __init__(self, l):
		self.l = l

	def accept(self, x):
		return not self.l(x)



class one_selector(selector):
	_eq = re.compile('^(.*)[.]eq[.](.*)$')
	_eqn = re.compile('^(.*)==(.*)$')
	_ne = re.compile('^(.*)[.]ne[.](.*)$')
	_nen = re.compile('^(.*)!=(.*)$')
	_ew = re.compile('^(.*)[.]endswith[.](.*)$')
	_sw = re.compile('^(.*)[.]startswith[.](.*)$')
	_ex = re.compile('^(.*)[.]exists[.]?$')
	def __init__(self, txt):
		if self._eq.match(txt):
			m = self._eq.match(txt)
			self.op = lambda t, k=m.group(1), v=m.group(2): t[k]==v
		elif self._ne.match(txt):
			m = self._ne.match(txt)
			self.op = lambda t, k=m.group(1), v=m.group(2): t[k]!=v
		elif self._eqn.match(txt):
			m = self._eqn.match(txt)
			self.op = lambda t, k=m.group(1), v=float(m.group(2)): float(t[k])==float(v)
		elif self._nen.match(txt):
			m = self._nen.match(txt)
			self.op = lambda t, k=m.group(1), v=float(m.group(2)): float(t[k])!=float(v)
		elif self._ew.match(txt):
			m = self._ew.match(txt)
			self.op = lambda t, k=m.group(1), v=m.group(2): t[k].endswith(v)
		elif self._sw.match(txt):
			m = self._sw.match(txt)
			self.op = lambda t, k=m.group(1), v=m.group(2): t[k].startswith(v)
		elif self._ex.match(txt):
			m = self._ex.match(txt)
			self.op = lambda t, k=m.group(1): t.has_key(k)
		else:
			die.die("Unrecognized operator: %s" % txt)

	def accept(self, item):
		return (self.op)(item)



def test():
	s = selector()
	s.select('a.eq.3')
	assert s.accept({'a': '3'})
	assert not s.accept({'a': '4'})
	s = selector()
	s.select('a.eq.3')
	s.select('b.ne.5')
	assert s.accept({'a': '3', 'b': '4'})
	assert s.accept({'a': '3', 'b': 'k'})
	assert not s.accept({'a': '3', 'b': '5'})
	assert not s.accept({'a': '2', 'b': '6'})
	assert not s.accept({'a': '2', 'b': '5'})
	s.or_another('a.eq.2')
	assert s.accept({'a': '2', 'b': '5'})
	s = selector()
	s.select('a.endswith.2')
	assert s.accept({'a': '2342'})



if __name__ == '__main__':
	test()
