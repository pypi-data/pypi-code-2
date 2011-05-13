#! python

"""
# comment  snames are in the form namespace.name   or name (in which case we prepend the namespace)
# or local.name in which case, name is just a local python variable.
# ...or @sname, in which case the sname must contain a string or tuple which is used as the sname.

# This sets the default namespace:
NAMESPACE name

#These are inputs and outputs for the entire file:
INPUTS sname sname sname
OUTPUTS sname sname sname

# Set a sname:
sname = EXEC python expression that does not involve snames

# Run a python function in a module:
sname,  sname = name.name.name(name=sname, ...)

# Run multiple variants of something:
FOR sname in snamelist
	@something that depends on name = ...something that depends on name

# Run a semiauto script (like this one) that does I/O via pickles.
sname,  sname = SCRIPT path/name(name=sname, ...)

# Monitor a file.   Proceed when the file is newer than the other.
# When no VIA is given, assume pickles.
# path/name may be @name, in which case name is a local python variable that evaluates to a string or tuple.
sname, sname = READ path/name NEWER_THAN path/name VIA python.function

# create or write the file when data is available.
# When no VIA is given, assume pickles.
WRITE path/name VIA python.function = ...all the options

SCRIPT
	WRITE path/name1 VIA python.function = ...all the options
	WRITE path/name2 VIA python.function = ...all the options
	PYTHON fname = tmpfile.tmpdir(...)
	EXEC script arguments
	ASYNC	# Optional.  This means the script could take a very long time.
		# This program won't wait for it, but it will check the next time it is run.
	sname, sname = READ path/name NEWER_THAN path/name VIA python.function
	# instead of NEWER_THAN, you can have FLAG which will proceed anyway, even if it
	# isn't newer than the requirements, but will flag the output as being a trial run.
	# It will still require that path/name be newer than the last time it was used.
	# You can also have CHECK python.function which checks to see if the value makes sense.

PYTHON
	chunk of python code

BEGIN
	def name(...)

	some python code

END
	some python code
"""
class ParseError(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)

class BadIndentError(ParseError):
	def __init__(self, *s):
		ParseError.__init__(self, *s)

class levels(object):
	p = re.compile('\s*')

	def __init__(self):
		self.current = 0
		self.lvl = ['']
	
	def map(self, s):
		sp = self.p.match(s).group(0)
		cmp = levels.cmp(self.lvl[self.current], sp)
		if cmp > 0:
			self.current += 1
			self.lvl[self.current] = sp
			return self.current
		elif cmp == 0:
			return self.current
		for i in range(self.current):
			tmp = levels.cmp(self.lvl[i], sp)
			if tmp == 0:
				self.current = i
				self.lvl = self.lvl[:i+1]
				return self.current
		raise BadIndentError, "Never before seen indentation level"

	@staticmethod
	def __count(a):
		spc = 0
		tc = 0
		for c in a:
			if c == ' ':
				spc += 1
			elif c == '\t':
				tc += 1
			else:
				raise BadIndentError("Whitespace that is not '\t' or ' '", c)
		return (spc, tc)
	
	@staticmethod
	def cmp(a, b):
		if a == b:
			return 0
		asp, at = levels.__count(a)
		bsp, bt = levels.__count(b)
		if asp==bsp and at==bt:
			return 0
		if at == bt:
			return cmp(asp, bsp)
		if at > bt and asp>=bsp:
			return 1
		if at < bt and asp<=bsp:
			return -1
		raise BadIndentError, "Cannot tell which is more indented."


class rule(object):
	def __init__(self, dependencies, targets, fcn, mapin, mapout):
		self.dependencies = set(mapin.keys())
		self.targets = set(mapout)
		self.mapin = mapin
		self.mapout = mapout
		self.fcn = fcn
		self.state = 0

	def fire(self, data):
		self.mapout.set(data, self.fcn( **self.mapin.go(data) ))

	def __hash__(self):
		return hash( ZZZZZ

class mapin(dict):
	def go(self, data):
		rv = {}
		for (k, v) in self.items():
			rv[v] = data[k]
		return rv

class ResettingVariable(Exception):
	def __init__(self, *s):
		Exception.__init__(self, s)


class mapout(list):
	def set(self, data, values):
		assert len(self) == len(values)
		for (s, v) in zip(self, values):
			if s in data and v != data[s]:
				raise ResettingVariable
			data[s] = v
		

class ruleset(object):
	def __init__(self, data, rules):
		self.data = data
		self.id = dictops.dict_of_sets()
		self.it = dictops.dict_of_sets()
		self.done = self.data.keys()
		self.needed = set()
		self.rules = set(rules)
		for rule in rules:
			for d in rule.dependencies:
				self.id.add(d, rule)
			for t in rule.targets:
				self.it.add(t, rule)
				self.needed.add(t)

	def go(self):
		fired = set()
		for r in self.rules:
			can = True
			for d in r.dependencies:
				if d not in self.done:
					can = False
					break
			if can:
				r.fire(self.data)
				fired.add(r)
		self.rules.difference_update(fired)
		return fired

####

class parser(object):
	def __init__(self):
		self.lvls = levels()
		self.n = 0
		self.txt = None
		self.indent = None

	def append(self, s):
		self.n += 1
		self.txt = s
		self.indent = self.lvls.map(s)
		

def parse(lines):
	n = 0
	indent = levels()
	ltmp = []
	is_c = False
	for line in lines:
		n += 1
		line = line.rstrip()
		lc = line.endswith('\\')
		if lc:
			line = line[:-1].rstrip()
		if is_c:
			ltmp.append(line_c(line.lstrip(), True, None, n))
		else:
			ltmp.append(line_c(line, False, indent.map(line), n))
		is_c = lc or ltmp[-1].is_open()
	

