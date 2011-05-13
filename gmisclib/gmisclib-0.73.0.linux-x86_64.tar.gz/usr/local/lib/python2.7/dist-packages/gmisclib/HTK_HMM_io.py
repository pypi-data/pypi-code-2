# -*- coding: utf-8 -*-
"""This reads in HMM files produced by HTK.
"""

import re
import sys
import numpy
import string
from gmisclib import g_encode


I = '  '

class BadFormatError(ValueError):
	def __init__(self, t, s):
		if t is not None:
			prefix = 'Line %d in %s: ' % (t.lnum, t.current.name)
		else:
			prefix = ''
		ValueError.__init__(self, '%s%s' % (prefix, s))




class vec(object):
	cname = {'u': 'Mean', 'v': 'Variance', 'i': 'InvCov', 't': 'TransP'}
	dim = {'u': 1, 'v': 1, 'i': -2, 't': 2}

	def __init__(self, vtype, v, name=None):
		"""@type vtype: string, one of 'u', 'v', 'i', 't'
		"""
		self.name = name
		self.v = v
		assert vtype in self.cname
		self.code = vtype
		self.id = hash((self.name, self.code, v.tostring()))
	
	def __eq__(self, other):
		return self.name==other.name and self.code==other.code and self.id==other.id
	
	def __hash__(self):
		return self.id
	
	def __repr__(self):
		return "<%s:%s %s>" % (self.code, self.name, str(self.v))

	def write(self):
		o = ['<%s> %d' % (self.cname[self.code], self.v.shape[0])]
		n = self.v.shape[0]
		title = self.cname[self.code]
		dim = self.dim[self.code]
		vec = self.v
		if dim == 1:
			assert len(vec.shape)==1
			tmp = [ '%.4f' % q for q in vec]
			o = [ I*4 + '<%s> %d' % (title, n),
				I*5 + ' '.join(tmp)
				]
		elif dim == -2:
			o = [ I*4 + '<%s> %d' % (title, n) ]
			for i in range(n):
				tmp = [ I*5 ]
				for j in range(i, n):
					tmp.append('%.3f' % vec[i,j])
				o.append(' '.join(tmp))
		elif dim == 2:
			o = [ I*4 + '<%s> %d' % (title, n) ]
			for i in range(n):
				tmp = [ I*5 ]
				for j in range(n):
					tmp.append('%.3f' % vec[i,j])
				o.append(' '.join(tmp))
		return o


class mixture(object):
	code = 'm'

	def __init__(self, wt=1.0, mean=None, var=None, name=None):
		self.name = name
		self.wt = wt
		self.m = mean
		self.v = var

	def __hash__(self):
		return hash((self.wt, self.m, self.v))
	
	def __eq__(self, other):
		return self.wt==other.wt and self.m==other.m and self.v==other.v

	def check(self):
		assert self.v is not None
		assert self.m is not None
		assert self.wt >= 0.0
		assert isinstance(self.v, vec) or isinstance(self.v, ref)
		assert isinstance(self.m, vec) or isinstance(self.m, ref)

	def __repr__(self):
		v0 = str(self.v)[:50]
		m0 = str(self.m)[:50]
		return "[M wt=%g mu=%s... v=%s...]" % (self.wt, m0, v0)

	def write(self, imix=None):
		o = []
		if imix is not None:
			o.append(I*3 + '<Mixture> %d %f' % (imix, self.wt)) 
			o.extend(self.m.write())
			o.extend(self.v.write())
		return o


class ref(object):
	def __init__(self, thing):
		assert thing.code is not None and thing.name is not None, "thing=%s" % repr(thing)
		self.thing = thing
		
	def write(self):
		return [I*4 + '~%s "%s"' % (self.thing.code, self.thing.name)]


def deref(x):
	if isinstance(x, ref):
		return x.thing
	return x


class state(object):
	def __init__(self, name=None):
		self.mx = [None, mixture()]
		self.name = name

	def create_mx(self, i):
		if i < len(self.mx):
			if self.mx[i] is None:
				self.mx[i] = mixture()
		else:
			self.mx.extend( [None] * (i-len(self.mx)) )
			self.mx.append( mixture() )
		return self.mx[i]

	def check(self, istate=-1, phone='???'):
		if self.mx[0] is not None:
			raise BadFormatError(None, "mixture[0] should be None in %s" % phone)
		for i in range(1, len(self.mx)):
			if self.mx[i] is None:
				raise BadFormatError(None, "mixture %d/%d not set in state %d of %s" % (i, len(self.mx), istate, phone))
			self.mx[i].check()

	def __repr__(self):
		return "<STATE %s>" % (', '.join([str(q) for q in self.mx]))
			
	def write(self, istate):
		o = []
		nmix = len(self.mx) - 1
		if istate is None:
			o.append(I*2 + '<NumMixes> %d' % nmix)
		else:
			o.append(I*2 + '<State> %d <NumMixes> %d' % (istate, nmix))
		for (i, mx) in enumerate(self.mx[1:]):
			o.extend(mx.write(i+1))
		return o




class hmm(object):
	def __init__(self, numstates, name=None):
		self.states = [ None ] * numstates
		self.t = None
		self.name = name

	def check(self):
		if self.states[0] is not None or self.states[1] is not None:
			raise BadFormatError(None, "State[0] and [1] should be None in %s" % self.name)
		for i in range(2, len(self.states)):
			if self.states[i] is None:
				raise BadFormatError(None, "State %d/%d not set in %s" % (i, len(self.states), self.name))
			self.states[i].check(istate=i, phone=self.name)
			
	def write(self):
		o = []
		for (i,s) in enumerate(self.states[2:]):
			o.extend(s.write(i+2))
		tr = self.t.write()
		nstates = len(self.states)
		return ['~h "%s"' % self.name, '<BeginHMM>',
				I*1 + '<NumStates> %d' % nstates
				] + o + tr + ['<EndHMM>']





class hmmset(object):
	def __init__(self):
		self.phones = []
		self.v_macros = {}
		self.u_macros = {}
		self.i_macros = {}
		self.s_macros = {}
		self.o_macro = {}

	def twiddle_o(self):
		om = self.o_macro
		si0, si1 = om['streaminfo']
		sourcekind = '_'.join([om['basekind']] + om['parmkind'])
		o = ['~o', '<STREAMINFO> %d %d' % (si0, si1),
			'<VECSIZE> %d' % om['vecsize'],
			 '<%s>' % om['durkind'],
			 '<%s>' % sourcekind
			]
		if 'covkind' in om:
			 o.append('<%s>' % covkind)
		return ' '.join(o)
	
	def write(self):
		o = [self.twiddle_o()]
		for (k, v) in self.v_macros.items():
			o.append('~v "%s"' % k)
			o.extend(v.write())
		for (k, v) in self.u_macros.items():
			o.append('~u "%s"' % k)
			o.extend(v.write())
		for (k, v) in self.i_macros.items():
			o.append('~i "%s"' % k)
			o.extend(v.write())
		for (k, v) in self.s_macros.items():
			o.append('~s "%s"' % k)
			o.extend(v.write())
		for p in self.phones:
			o.extend( p.write())
		return o


class tokstream(object):
	"""This breaks the HTK HMM file down into tokens."""

	int = re.compile('([+-]?\d+)')
	float = re.compile('([+-]?[0-9]*[.][0-9]*[e0-9+-]*)')
	bracket = re.compile('<\s*(\w+)\s*>')
	macro = re.compile('~([a-zA-Z])')
	name = re.compile('"([a-zA-Z_]\w*)"')

	def __init__(self, fdlist):
		self.fds = list(fdlist)
		if self.fds:
			self.current = self.fds.pop(0)
		else:
			self.current = None
		self.lnum = 0
		self.nextline()
		self.fulltok = None

	def _getline(self):
		if self.current is None:
			return None
		while True:
			line = self.current.readline()
			self.lnum += 1
			if line == '':
				return None
			else:
				line = line.strip()
			if line != '':
				return line

	def nextline(self):
		"""Get the next line from the input files(s).  Sets self.line.
		@return: the line.
		@rtype: str or L{None}.
		"""
		self.line = self._getline()
		if self.line is None:
			if self.fds:
				self.current = self.fds.pop(0)
				self.lnum = 0
				self.line = self._getline()
			else:
				self.line = None
		return self.line


	def __nonzero__(self):
		"""@return: True when there is more work to be done."""
		return self.line is not None

	def get(self):
		"""Get a token.
		This also sets C{self.fulltok} with the full text of the token.
		@raise BadFormatError: When the remainder of the line doesn't match any legal pattern.
		@return: The regular expression that matches the next token, and the relevant text.
		@rtype: (compiled regular expression, str)
		"""
		assert self.line is not None
		for pat in [self.macro, self.bracket, self.float, self.int, self.name]:
			m = pat.match(self.line)
			if m:
				self.line = self.line[m.end():].strip()
				if self.line == '':
					self.nextline()
				tok = m.group(1)
				if pat is self.bracket:
					tok = tok.lower()
				self.fulltok = m.group(0)
				return (pat, tok)
		raise BadFormatError(self, "Cannot match remainder of line: '%s'" % self.line)

	def get_name(self):
		p, tok = self.get()
		if p is not self.name:
			raise BadFormatError(self, "Expected a name, got %s" % self.fulltok)
		return tok

	def get_bracket(self):
		p, tok = self.get()
		if p is not self.bracket:
			raise BadFormatError(self, "Expected a bracket, got %s" % self.fulltok)
		return tok

	def get_int(self):
		p, tok = self.get()
		if p is not self.int:
			raise BadFormatError(self, "Expected an int, got %s" % self.fulltok)
		return int(tok)

	def get_float(self):
		p, tok = self.get()
		if p is not self.float and p is not self.int:
			raise BadFormatError(self, "Expected a float, got %s" % self.fulltok)
		return float(tok)





def read_floats_t(vtype, dim, t, tok, phoneme='???'):
	n = t.get_int()
	return read_vec(dim, n, t, vtype=vtype)


def read_floats_b(vtype, dim, t, tok, phoneme='???', name=None):
	if t.get_bracket() != vec.cname[vtype].lower():
		raise BadFormatError(t, 'macro "%s" expects a <variance> tag (phoneme=%s)' % (tok, phoneme))
	n = t.get_int()
	return read_vec(dim, n, t, vtype=vtype, name=name)


def read_vec(dim, n, t, name=None, vtype=None):
	if dim == 1:
		tmp = numpy.zeros((n,))
		for i in range(n):
			tmp[i] = t.get_float()
	elif dim == -2:
		tmp = numpy.zeros((n,n))
		for i in range(n):
			for j in range(i, n):
				tmp[i,j] = t.get_float()
		for i in range(n):
			for j in range(i+1, n):
				tmp[j,i] = tmp[i,j]
	elif dim == 2:
		tmp = numpy.zeros((n,n))
		for i in range(n):
			for j in range(n):
				tmp[i,j] = t.get_float()
	else:
		raise AssertionError, "Never happens"
	return vec(vtype, tmp, name)






def read(fdlist):
	rv = hmmset()
	phoneme = None
	statenum = None
	mixnum = None
	thishmm = None
	thisstate = None
	thismix = None
	t = tokstream(fdlist)
	while t:
		pat, tok = t.get()
		if pat is t.macro:
			if tok == 'h':
				phoneme = t.get_name()
			elif tok == 'o':
				rv.o_macro = {}
			elif tok == 'u' and thismix is not None:
				try:
					thismix.m = ref(rv.u_macros[t.get_name()])
				except KeyError, x:
					raise BadFormatError(t, "undefined macro ~%s '%s' in phoneme %s" % (tok, x, phoneme))
			elif tok == 'u':
				name = t.get_name()
				rv.u_macros[name] = read_floats_b('u',  1, t, tok, '---', name=name)
			elif tok == 'v' and thismix is not None:
				try:
					thismix.v = ref(rv.v_macros[t.get_name()])
				except KeyError, x:
					raise BadFormatError(t, "undefined macro ~%s '%s' in phoneme %s" % (tok, x, phoneme))
			elif tok == 'v':
				name = t.get_name()
				rv.v_macros[name] = read_floats_b('v', 1, t, tok, '---', name=name)
			elif tok == 'i' and thismix is not None:
				try:
					thismix.v = ref(rv.i_macros[t.get_name()])
				except KeyError, x:
					raise BadFormatError(t, "undefined macro ~%s '%s' in phoneme %s" % (tok, x, phoneme))
			elif tok == 'i':
				name = t.get_name()
				rv.i_macros[name] = read_floats_b('i',  -2, t, tok, '---', name=name)
			elif tok == 's' and statenum is not None:
				name = t.get_name()
				assert thishmm is not None
				thishmm.states[statenum] = rv.s_macros[t.get_name()]
			elif tok == 's':
				assert 0
		elif pat is t.bracket and tok=='gconst':
			t.get_float()
		elif pat is t.bracket and tok=='streaminfo':
			rv.o_macro['streaminfo'] = (t.get_int(), t.get_int())
		elif pat is t.bracket and tok=='vecsize':
			rv.o_macro['vecsize'] = t.get_int()
		elif pat is t.bracket and tok=='beginhmm':
			if phoneme is None:
				raise BadFormatError(t, "phoneme not named at BeginState")
			if t.get_bracket() != 'numstates':
				raise BadFormatError(t, "Expected numstates, got <%s>" % tok)
			numstates = t.get_int()
			if not (numstates > 0):
				raise BadFormatError(t, "numstates out of range: 0<%d for phoneme %s" % (numstates, phoneme))
			thishmm = hmm(numstates, phoneme)
		elif pat is t.bracket and tok=='state':
			if numstates is None:
				raise BadFormatError(t, "numstates not set before state")
			thisstate = state()
			statenum = t.get_int()
			thishmm.states[statenum] = thisstate
			if not (statenum>1 and statenum<= numstates):
				raise BadFormatError(t, "State number out of range: 1<%d<%d" % (statenum, numstates))
			mixnum = 1
			nummixes = 1
			thismix = thisstate.create_mx(mixnum)
		elif pat is t.bracket and tok=='nummixes':
			if thisstate is None:
				raise BadFormatError(t, "state not set before nummixes")
			nummixes = t.get_int()
			if not (nummixes > 0):
				raise BadFormatError(t, "nummixes out of range: 0<%d for state %d" % (nummixes, statenum))
		elif pat is t.bracket and tok=='mixture':
			if statenum is None:
				raise BadFormatError(t, "state not set before mixture")
			nummixes = None
			mixnum = t.get_int()
			thismix = thisstate.create_mx(mixnum)
			thismix.wt = t.get_float()
		elif pat is t.bracket and tok=='transp':
			n = t.get_int()
			if n != numstates:
				raise BadFormatError(t, "transp: size mismatch: %d != %d" % (n, numstates))
			thishmm.t = read_vec(2, numstates, t, vtype='t')
		elif pat is t.bracket and tok=='endhmm':
			thisstate = None
			mixnum = None
			thishmm.check()
			rv.phones.append(thishmm)
			thishmm = None
			phoneme = None
		elif thismix is not None and pat is t.bracket and tok=='variance':
			thismix.v = read_floats_t('v', 1, t, tok, phoneme)
		elif thismix is not None and pat is t.bracket and tok=='mean':
			thismix.m = read_floats_t('u', 1, t, tok, phoneme)
		elif thismix is not None and pat is t.bracket and tok=='invcov':
			thismix.v = read_floats_t('i', -2, t, tok, phoneme)
		elif pat is t.bracket and tok in ['diagc', 'invdiagc', 'fullc', 'lltc', 'xformc']:
			rv.o_macro['covkind'] = tok
		elif pat is t.bracket and tok in [ 'nulld', 'poissond', 'gammad', 'gend']:
			rv.o_macro['durkind'] = tok
		elif pat is t.bracket and tok=='user':
			rv.o_macro['basekind'] = tok
			rv.o_macro['parmkind'] = ''
		elif pat is t.bracket and '_' in tok:
			klist = tok.split('_')
			rv.o_macro['basekind'] = klist[0]
			rv.o_macro['parmkind'] = klist[1:]
		else:
			raise BadFormatError(t, "Unexpectedly saw %s." % t.fulltok)

	return rv


class NoPhonemeToFormat(ValueError):
	def __init__(self, *s):
		ValueError.__init__(self, *s)

_e = g_encode.encoder(allowed=string.letters+string.digits, eschar='_')
_needsq = re.compile('(^[0-9])|[A-Z]')
_q = re.compile('q')

def HTKformat(s):
	"""Format for HTK state name."""
	assert isinstance(s, str), "s=%s" % repr(s)
	if not s:
		raise NoPhonemeToFormat("lbl='%s'" % s)
	s = _q.sub('qq', s)
	s = _needsq.sub(lambda x: 'q%s' % x.group(0).lower(), s)
	return _e.fwd(s)


_brkt = re.compile(r'\[|\]|%')
def dict_format(s):
	"""Format for center [bracket] in HTK dictionary."""
	assert isinstance(s, str), "s=%s" % repr(s)
	if not s:
		raise NoPhonemeToFormat("lbl='%s'" % s)
	return _brkt.sub(lambda x: '%%%d' % ord(x.group(0)), s)



_TEST = """
~o
<STREAMINFO> 1 26
<VECSIZE> 26<NULLD><MFCC_E_D><DIAGC>
~v "b"
<VARIANCE> 26
 6.262400e+01 5.858900e+01 1.003000e+02 7.347500e+01 6.431700e+01 5.047400e+01 6.242300e+01 4.893200e+01 5.247800e+01 3.391300e+01 3.731700e+01 3.165200e+01 4.400000e-02 5.378000e+00 5.956000e+00 6.876000e+00 6.459000e+00 6.584000e+00 6.842000e+00 6.603000e+00 5.119000e+00 5.212000e+00 4.712000e+00 4.471000e+00 3.459000e+00 5.000000e-03
~o <STREAMINFO> 1 26 <VECSIZE> 26 <NULLD><MFCC_E_D>
~h "b"
<BeginHMM>
  <NumStates> 6
    <State> 2 <NumMixes> 1
      <Mixture> 1 1
        <Mean> 26
          0.939 6.000 9.331 -4.474 -9.654 -4.482 -9.613 -2.793 -1.901 -0.622 -2.544 -3.954 0.786 0.413 -0.327 0.125 -1.229 -0.422 0.067 -0.052 -0.266 -0.783 -0.376 -0.270 -0.252 0.020
        ~v "b"
    <State> 3 <NumMixes> 1
      <Mixture> 1 1
        <Mean> 26
          0.909 6.071 9.146 -4.544 -9.690 -4.453 -9.601 -2.748 -1.946 -0.706 -2.698 -3.882 0.790 0.401 -0.369 0.164 -1.257 -0.419 0.133 -0.073 -0.286 -0.796 -0.369 -0.296 -0.248 0.020
        ~v "b"
    <State> 4 <NumMixes> 1
      <Mixture> 1 1
        <Mean> 26
          0.823 5.966 9.268 -4.783 -9.793 -4.583 -9.584 -2.669 -2.134 -0.603 -2.607 -3.922 0.784 0.424 -0.337 0.192 -1.219 -0.428 0.100 -0.100 -0.311 -0.810 -0.350 -0.268 -0.270 0.020
        ~v "b"
    <State> 5 <NumMixes> 1
      <Mixture> 1 1
        <Mean> 26
          0.891 6.011 9.190 -4.533 -9.694 -4.507 -9.363 -2.863 -2.066 -0.611 -2.551 -3.939 0.785 0.430 -0.344 0.155 -1.231 -0.445 0.104 -0.034 -0.269 -0.785 -0.371 -0.272 -0.261 0.020
        ~v "b"
<TransP> 6
  0.0000 1.0000 0.0000 0.0000 0.0000 0.0000
  0.0000 0.8000 0.2000 0.0000 0.0000 0.0000
  0.0000 0.0000 0.8000 0.2000 0.0000 0.0000
  0.0000 0.0000 0.0000 0.8000 0.2000 0.0000
  0.0000 0.0000 0.0000 0.0000 0.8000 0.2000
  0.0000 0.0000 0.0000 0.0000 0.0000 0.0000
<EndHMM>
"""


def test():
	fd = fake_file.file(name='-')
	fd.write(_TEST)
	fd.seek(0)
	t2 = '\n'.join( read([fd]).write() )
	fd2 = fake_file.file(name='-')
	fd2.write(t2)
	fd2.seek(0)
	t3 = '\n'.join( read([fd2]).write() )
	assert t2==t3
	return t2


if __name__ == '__main__':
	from gmisclib import fake_file
	print test()
	# read([open(q, 'r') for q in sys.argv[1:]])
