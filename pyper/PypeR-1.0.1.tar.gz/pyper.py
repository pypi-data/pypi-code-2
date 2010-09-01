#!/usr/bin/env python
'''
         PypeR (PYthon-piPE-R)

This package provides a light-weight interface to use R in Python by pipe.  It
can be used on multiple platforms since it is written in pure python. 

Prerequisites:
	1. Python 2.4 or later is required since PypeR uses the python standard
	   module "subprocess", which was first introduced in Python 2.4.
	2. On Windows, the pywin32 package is required.

Usage:
	The usage of this packages is very simple. Examples are presented in the
	file "test.py" in the distribution package.

	PypeR provide a class "R" to wrap the R language. An instance of the R
	class is used to manage an R process. Different instances can use different
	R installations. On POSIX systems (including the Cygwin environment on
	Windows), it is even possible to use an R installed on a remote computer. 
	
	Basicly, there are four ways to use an instance of the R class.

	1. Use the methods of the instance
		methods include:
			run:This method is used to pass an R command string to the R process,
				the return value is a string - the standard output from R. Note
				that the return value usually includes the R expression (a
				series of R codes) themselves and the output of the R
				expression.  If the real result value is wanted, use the
				function "get" instead.  
			assign: Assign a value to an R variable. No return value.  
			get: Get the result of an R expression. 
			remove: Remove a R variable.

	2. Call the instance as a function
		The instance is callable. If called as a function, it behaves just
		same as its "run" method.

	3. Use the instance as a Python dictionary
		The instance can mimic some operations on a python dictionary,
		typically, to assign values to R variables, to retrieve values for any
		R expression, or delete an R variable. These two operations do same
		jobs as the methods "assign", "get", and "remove".

	4. Access R variables as if they are the attributes of the instance.
		If the variable name cannot be found in the instance or its class, the
		instance will try to get/set/remove it in R. This way is similar to 3,
		but with more limitations, e.g., the R variable name cannot contain any
		DOT (.) 
	
	Considering that any code block in R is an expression, the "get" method (or
	the form of retrieving values from a dictionary) can be used to run a
	number of R commands with the final result returned. 

	Note that PypeR do NOT validate/convert a variable name when pass it to R.
	If a variable name with a leading underscore ("_"), although it legal in
	python, is passed to R, an RError will be raised.
	

DEBUG model:
	Since the child process (R) can be easily killed by any ocassional error in
	the codes passed to it, PypeR is set to "DEBUG" model by default. This
	means that any code blocks send to R will be wrapped in the function
	"try()", which will prevent R from crashing. To disable the "DEBUG" model,
	the user can simple set the variable "_DEBUG_MODE" in the R class or in its
	instance to False. 

	To model the behavior of the "get" method of a Python dictionary, the
	method "get" allows wild values for variables that does not exists in R.
	Then the R expression will always be wrapped in "try()" to avoid R crashing
	if the method "get" is called.  
'''

# the module "subprocess" requires Python 2.4

import os
import sys
import time
import re
import tempfile
from types import *
import subprocess
import shlex
from pipeio import Popen, PIPE, send_all, recv_some

if sys.version < '2.3':
	set = frozenset = tuple
elif sys.version < '2.4':
	from sets import Set as set, ImmutableSet as frozenset

try:
	import numpy
	has_numpy = True
except:
	has_numpy = False

__version__ = '1.0.1'

def NoneStr(obj): return 'NULL'

def BoolStr(obj): return obj and 'TRUE' or 'FALSE'

def ReprStr(obj): return repr(obj)

def LongStr(obj):  
	rtn = repr(obj)
	if rtn[-1] == 'L': rtn = rtn[:-1]
	return rtn

def ComplexStr(obj):
	return repr(obj).replace('j', 'i')

def SeqStr(obj, head='c(', tail=')'):
	if not obj: return head + tail
	# detect types
	if isinstance(obj, set):
		obj = list(obj)
	obj0 = obj[0]
	tp0 = type(obj0)
	simple_types = [str, bool, int, long, float, complex]
	num_types = [int, long, float, complex]
	is_int = tp0 in (int, long) # token for explicit converstion to integer in R since R treat an integer from stdin as double
	if tp0 not in simple_types: head = 'list('
	else:
		tps = isinstance(obj0, basestring) and [StringType] or num_types
		for i in obj[1:]:
			tp = type(i)
			if tp not in tps:
				head = 'list('
				is_int = False
				break
			elif is_int and tp not in (int, long):
				is_int = False
	# convert
	return (is_int and 'as.integer(' or '') + head + ','.join(map(Str4R, obj)) + tail + (is_int and ')' or '') 

def DictStr(obj):
	return 'list(' + ','.join(map(lambda a:'%s=%s' % (Str4R(a[0]), Str4R(a[1])), obj.items())) + ')'

def OtherStr(obj):
	if has_numpy:
		if isinstance(obj, numpy.ndarray):
			shp = obj.shape
			tpdic = {'i':'as.integer(c(%s))', 'u':'as.integer(c(%s))', 'f':'as.double(c(%s))', 'c':'as.complex(c(%s))', 'b':'c(%s)', 'S':'c(%s)', 'a':'c(%s)', 'U':'c(%s)', 'V':'list(%s)'} # in order: (signed) integer, unsigned integer, float, complex, boolean, string, string, unicode, anything

			def getVec(ary):
				tp = ary.dtype.kind
				rlt = ary.reshape(reduce(lambda a,b=1:a*b, ary.shape))
				rlt = tp == 'b' and map(lambda a:a and 'TRUE' or 'FALSE', rlt) or rlt.tolist()
				if tp != 'V':
					return tpdic.get(tp, 'c(%s)') % repr(rlt)[1:-1]
				# record array
				rlt = map(SeqStr, rlt) # each record will be mapped to vector or list
				return tpdic.get(tp, 'list(%s)') % (', '.join(rlt)) # use str here instead of repr since it has already been converted to str by SeqStr

			if len(shp) == 1: # to vector
				tp = obj.dtype
				if tp.kind != 'V': 
					return getVec(obj)
				# One-dimension record array will be converted to data.frame
				def mapField(f):
					ary = obj[f]
					tp = ary.dtype.kind
					return '"%s"=%s' % (f, tpdic.get(tp, 'list(%s)') % repr(ary.tolist())[1:-1])
				return 'data.frame(%s)' % (', '.join(map(mapField, tp.names)))
			elif len(shp) == 2: # two-dimenstion array will be converted to matrix
				return 'matrix(%s, nrow=%d, byrow=TRUE)' % (getVec(obj), shp[0])
			else: # to array
				dim = list(shp[-2:]) # row, col
				dim.extend(shp[-3::-1])
				newaxis = range(len(shp))
				newaxis[-2:] = [len(shp)-1, len(shp)-2]
				return 'array(%s, dim=c(%s))' % (getVec(obj.transpose(newaxis)), repr(dim)[1:-1])
			# record array and char array
	if hasattr(obj, '__iter__'): # for iterators
		if hasattr(obj, '__len__') and len(obj) <= 10000:
			return SeqStr(list(obj))
		else: # waiting for better solution for huge-size containers
			return SeqStr(list(obj))
	return repr(obj)

base_tps = [NoneType, bool, int, long, float, complex, str, unicode, list, tuple, set, frozenset, dict]
base_tps.reverse()
str_func = {NoneType:NoneStr, bool:BoolStr, int:repr, long:LongStr, float:repr, complex:ComplexStr, str:repr, unicode:repr, list:SeqStr, tuple:SeqStr, set:SeqStr, frozenset:SeqStr, dict:DictStr}

def Str4R(obj):  
	'''
	convert a Python basic object into an R object in the form of string.
	'''
	#return str_func.get(type(obj), OtherStr)(obj) 
	if type(obj) in str_func:
		return str_func[type(obj)](obj)
	for tp in base_tps:
		if isinstance(obj, tp):
			return str_func[tp](obj)
	return OtherStr(obj)

class RError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class R: # (object):
	'''
	A Python class to enclose an R process.
	'''
	__Rfun = '''.getRvalue4Python__ <- function(x) {
	has_numpy <- %s
	if (has_numpy) {
		headstr <- 'numpy.array('
		tailstr <- ')'}
	else headstr <- tailstr <- ''
	NullStr <- function(x) 'None'
	VectorStr <- function(x) {
		complx <- is.complex(x)
		if (is.character(x)) x <- paste('"', x, '"', sep='')
		if (length(x)==1) x <- paste(x)
		else x <- paste(headstr, '[', paste(x, collapse=', '), ']', tailstr, sep='')
		if (complx) x <- gsub('i', 'j', x)
		return(x) }
	MatrixStr <- function(x) {
		complx <- is.complex(x)
		if (is.character(x)) x <- matrix(paste('"', x, '"', sep=''), nrow=nrow(x))
		x <- apply(x, 1, function(r) paste('[', paste(r, collapse=', '), ']', sep=''))
		x <- paste(headstr, '[', paste(x, collapse=', '), ']', tailstr, sep='')
		if (complx) x <- gsub('i', 'j', x)
		return(x) }
	ArrayStr <- function(x) {
		complx <- is.complex(x)
		ndim <- length(dim(x))
		if (ndim == 1) return(VectorStr(x))
		if (ndim == 2) return(MatrixStr(x))
		# ndim >= 3
		if (is.character(x)) x <- array(paste('"', x, '"', sep=''), dim=dim(x))
		for (i in seq(ndim-1)) 
			x <- apply(x, seq(dim(x))[-1], function(r) paste('[', paste(r, collapse=', '), ']', sep=''))
		x <- paste(headstr, '[', paste(x, collapse=', '), ']', tailstr, sep='')
		if (complx) x <- gsub('i', 'j', x)
		return(x) }
	DataFrameStr <- function(x) {
		cnms <- colnames(x) # get column names
		ctp <- list()
		for (i in seq(x)) {
			xi <- as.vector(x[[i]])
			if (is.character(xi)) {
				ctp[i] <- sprintf('("%%s", "|S%%d")', cnms[i], max(nchar(xi)) )
				xi <- paste('"', xi, '"', sep='') }
			else if (is.logical(xi)) {
				xi <- ifelse(xi, 'True', 'False')
				ctp[i] <- paste('("', cnms[i], '", "<?")' ) }
			else if (is.integer(xi)) {
				xi <- paste(xi)
				ctp[i] <- paste('("', cnms[i], '", "<q")' ) }
			else if (is.double(xi)) {
				xi <- paste(xi)
				ctp[i] <- paste('("', cnms[i], '", "<g")' ) }
			else if (is.complex(xi)) {
				xi <- gsub('i', 'j', paste(xi))
				ctp[i] <- paste('("', cnms[i], '", "<G")') }
			x[[i]] <- xi }
		x <- as.matrix(x)
		x <- apply(x, 1, function(r) paste('(', paste(r, collapse=', '), ')', sep=''))
		if (has_numpy) {
			tailstr <- paste(', dtype=[', paste(ctp, collapse=', '), ']', tailstr, sep='')
			}
		x <- paste(headstr, '[', paste(x, collapse=', '), ']', tailstr, sep='')
		return(x) }
	ListStr <- function(x) {
		nms <- names(x) # get column names
		x <- sapply(x, Str4Py)
		if (!is.null(nms)) {
			nms <- paste('"', nms, '"', sep='')
			x <- sapply(seq(nms), function(i) paste('(', nms[i], ',', x[i], ')') ) }
		x <- paste('[', paste(x, collapse=', '), ']', sep='')
		return(x) }
	Str4Py <- function(x) {
		# no considering on NA, Inf, ...
		# use is.XXX, typeof, class, mode, storage.mode, sprintf
		if (is.factor(x)) x <- as.vector(x)
		if (is.null(x)) return(NullStr(x))
		if (is.vector(x) && !is.list(x)) return(VectorStr(x))
		if (is.matrix(x) || is.array(x)) return(ArrayStr(x))
		if (is.data.frame(x)) return(DataFrameStr(x))
		if (is.list(x)) return(ListStr(x))
		return(NullStr(x)) }
	Str4Py(x)
	}
	# initalize library path for TCL/TK based environment on Windows, e.g. Python IDLE
	.addLibs <- function() {
		ruser <- Sys.getenv('R_USER')
		userpath <- Sys.getenv('R_LIBS_USER')
		libpaths <- .libPaths()
		for (apath in userpath) {
			if (length(grep(apath, libpaths)) > 0) next
			apath <- paste(ruser, '/Documents', substr(apath, nchar(ruser)+1, nchar(apath)), sep='')
			.libPaths(apath)
			}
		}
	if(identical(.Platform$OS.type, 'windows')) .addLibs()
	rm(.addLibs)
	''' 
	_DEBUG_MODE = True

	def __init__(self, RCMD='R', wait0=2, wait=0.01, max_len=1000, use_numpy=True, host='localhost', user=None, ssh='ssh', return_err=True):
		'''
		RCMD: The name of a R interpreter, path information should be included
			if it is not in the system search path.
		wait0: The time span for recv_some to receive data from pipe for the
			first time
		wait: The time span for recv_some to receive data from pipe max_len:
			define the upper limitation for the length of command string.  A
			command string will be passed to R by a temporary file if it is
			longer than this value.
		use_numpy: Used as a boolean value. A False value will disable numpy
			even if it has been imported.
		host: The computer name (or IP) on which the R interpreter is
			installed. The value "localhost" means that R locates on the the
			localhost computer. On POSIX systems (including Cygwin environment
			on Windows), it is possible to use R on a remote computer if the
			command "ssh" works. To do that, the user needs to set this value,
			and perhaps the parameter "user".
		user: The user name on the remote computer. This value needs to be set
			only if the user name on the remote computer is different from the
			local user. In interactive environment, the password can be input
			by the user if prompted. If running in a program, the user needs to
			be able to login without typing password! 
		ssh: The program to login to remote computer.
		return_err: redict stderr to stdout
		''' 
		# use self.__dict__.update to register variables since __setattr__ is
		# used to set variables for R.  tried to define __setattr in the class,
		# and change it to __setattr__ for instances at the end of __init__,
		# but it seems failed.
		# -- maybe this only failed in Python2.5? as warned at
		# http://wiki.python.org/moin/NewClassVsClassicClass: 
		# "Warning: In 2.5, magic names (typically those with a double
		# underscore (DunderAlias) at both ends of the name) may look at the
		# class rather than the instance even for old-style classes."
		self.__dict__.update({
			'wait0':wait0, 
			'wait':wait, 
			'max_len':max_len, 
			'localhost':host=='localhost', 
			'tail':sys.platform=='win32' and '\r\n' or '\n'})

		RCMD = shlex.split(RCMD) #re.split(r'\s', RCMD)
		if not self.localhost:
			RCMD.insert(0, host)
			if user:
				RCMD.insert(0, '-l%s' % user)
			RCMD.insert(0, ssh)
		#args = ('--vanilla',) # equal to --no-save, --no-restore, --no-site-file, --no-init-file and --no-environ
		args = ('--quiet', '--no-save', '--no-restore') # "--slave" cannot be used on Windows!
		for arg in args:
			if arg not in RCMD: RCMD.append(arg)
		if hasattr(subprocess, 'STARTUPINFO'):
			info = subprocess.STARTUPINFO()
			info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			info.wShowWindow = subprocess.SW_HIDE
		else: info = None
		self.__dict__.update({
			'prog':Popen(RCMD, stdin=PIPE, stdout=PIPE, stderr=return_err and subprocess.STDOUT or None, startupinfo=info), 
			'has_numpy':use_numpy and has_numpy, 
			'Rfun':self.__class__.__Rfun % ((use_numpy and has_numpy) and 'TRUE' or 'FALSE')})
		self.__call__(self.Rfun)
		to_discard = recv_some(self.prog, e=0, t=wait0)

	def __runOnce(self, CMD, use_try=None):
		'''
		CMD: a R command string
		'''
		use_try = use_try or self._DEBUG_MODE
		tail = self.tail
		tail_token = 'R command at time: %s' % repr(time.time())
		tail_cmd = 'print("%s")%s' % (tail_token, tail)
		rlt_tail = '> print("%s")%s[1] "%s"%s> ' % (tail_token, tail, tail_token, tail)
		rlt_tail1 = rlt_tail.replace('\r', '') # sometimes Windows use '\n' only, e.g. after "library(fastICA)"!
		#if not CMD.endswith(tail): CMD = CMD + tail
		if len(CMD) <= self.max_len or not self.localhost: 
			fn = None
		else:
			fh, fn = tempfile.mkstemp()
			os.fdopen(fh, 'wb').write(CMD)
			CMD = 'source("%s")' % fn.replace('\\', '/')
		CMD = (use_try and 'try({%s})%s%s' or '%s%s%s') % (CMD, tail, tail_cmd)
		send_all(self.prog, CMD)
		rlt = ''
		while not rlt.endswith(rlt_tail) and not rlt.endswith(rlt_tail1):
			try:
				rltonce = recv_some(self.prog, e=1, t=self.wait)
				if rltonce: rlt = rlt + rltonce
			except: break
		else: rlt = rlt[:-len(rlt_tail)]
		if fn is not None:
			os.unlink(fn)
		return rlt

	def __call__(self, CMDS=[], use_try=None):
		'''
		Run a (list of) R command(s), and return the output message from the STDOUT of R.

		CMDS: an R command string or a list of R commands
		'''
		rlt = []
		if isinstance(CMDS, basestring): # a single command
			rlt.append(self.__runOnce(CMDS, use_try=use_try))
		else: # should be a list of commands
			for CMD in CMDS: 
				rlt.append(self.__runOnce(CMD, use_try=use_try))
		if len(rlt) == 1: rlt = rlt[0]
		return rlt

	def __getitem__(self, obj, use_try=None):
		'''
		Get the value of an R variable or expression. The return value is
		converted to the corresponding Python object.

		obj: a string - the name of an R variable, or an R expression
		use_try: use "try" function to wrap the R expression. This can avoid R
			crashing if the obj does not exist in R.
		'''
		if obj.startswith('_'):
			raise RError('Leading underscore ("_") is not permitted in R variable names!')
		use_try = use_try or self._DEBUG_MODE
		cmd = '.getRvalue4Python__(%s)' % obj
		rlt = self.__call__(cmd, use_try=use_try)
		head = len((use_try and 'try({%s})%s[1] ' or '%s%s[1] ') % (cmd, self.tail)) 
		tail = len(rlt) - len(self.tail) # - len('"')
		try:
			rlt = eval(eval(rlt[head:tail]))
		except:
			raise RError(rlt)
		return rlt

	def __setitem__(self, obj, val):
		'''
		Assign a value (val) to an R variable (obj).

		obj: a string - the name of an R variable
		val: a python object - the value to be passed to an R object
		'''
		if obj.startswith('_'):
			raise RError('Leading underscore ("_") is not permitted in R variable names!')
		self.__call__('%s <- %s' % (obj, Str4R(val)))

	def __delitem__(self, obj):
		if obj.startswith('_'):
			raise RError('Leading underscore ("_") is not permitted in R variable names!')
		self.__call__('rm(%s)' % obj)

	def __del__(self):
		send_all(self.prog, 'q("no")'+self.tail)
		self.prog = None

	def __getattr__(self, obj):
		'''
		obj: a string - the name of an R variable
		'''
		try:
			rlt = self.__getitem__(obj)
		except:
			raise RError('No this object!')
		return rlt

	def __setattr__(self, obj, val):
		if obj in self.__dict__ or obj in self.__class__.__dict__: # or obj.startswith('_'):
			self.__dict__[obj] = val # for old-style class
			#object.__setattr__(self, obj, val) # for new-style class
		else:
			self.__setitem__(obj, val)

	def __delattr__(self, obj):
		if obj in self.__dict__:
			del self.__dict__[obj]
		else:
			self.__delitem__(obj)

	def get(self, obj, default=None):
		'''
		obj: a string - the name of an R variable, or an R expression
		default: a python object - the value to be returned if failed to get data from R
		'''
		try:
			rlt = self.__getitem__(obj, use_try=True)
		except:
			if True: #val is not None:
				rlt = default
			else:
				raise RError('No this object!')
		return rlt

	run, assign, remove = __call__, __setitem__, __delitem__


# for a single-round duty:
def runR(CMDS, Robj='R', wait0=2, wait=0.01, max_len=1000, use_numpy=True, host='localhost', user=None, ssh='ssh'):
	'''
	Run a (list of) R command(s), and return the output from the STDOUT.

	CMDS: a R command string or a list of R commands.
	Robj: can be a shell command (like /usr/bin/R), or the R class.
	wait0: The time span for recv_some to receive data from pipe for the first
		time.
	wait: The time span for recv_some to receive data from pipe.
	max_len: define the upper limitation for the length of command string. A
		command string will be passed to R by a temporary file if it is longer
		than this value.
	use_numpy: Used as a boolean value. A False value will disable numpy even
		if it has been imported.
	host: The computer name (or IP) on which the R interpreter is
		installed. The value "localhost" means that the R locates on the
		the localhost computer. On POSIX systems (including Cygwin
		environment on Windows), it is possible to use R on a remote
		computer if the command "ssh" works. To do that, the user need set
		this value, and perhaps the parameter "user".
	user: The user name on the remote computer. This value need to be set
		only if the user name is different on the remote computer. In
		interactive environment, the password can be input by the user if
		prompted. If running in a program, the user need to be able to
		login without typing password! 
	ssh: The program to login to remote computer.
	'''
	if isinstance(Robj, basestring):
		Robj = R(RCMD=Robj, wait0=wait0, wait=wait, max_len=max_len, host=host, user=user, ssh=ssh)
	rlt = Robj.run(CMDS=CMDS)
	if len(rlt) == 1: rlt = rlt[0]
	return rlt
	

