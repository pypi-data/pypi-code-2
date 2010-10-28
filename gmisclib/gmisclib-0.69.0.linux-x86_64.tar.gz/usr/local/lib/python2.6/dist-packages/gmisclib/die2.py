



import inspect
import sys
import traceback

debug = True	# Set to False to disable dbg() messages.
compress = True

_name = sys.argv[0]
_ni = _name.rfind('/')
if _ni >=0 and _ni != len(_name)-1:
	_name = _name[_ni+1:]

logfd = sys.stderr

_last = ()
_counter = 0


def note(name, val):
	stack = inspect.stack()
	uplocal = stack[1][0].f_locals
	stack = None
	if not uplocal.has_key('__note'):
		uplocal['__note'] = {}
	uplocal['__note'][name] = val
	uplocal = None


def show(name):
	stack = inspect.stack()
	uplocal = stack[1][0].f_locals
	stack = None
	if not uplocal.has_key('__show'):
		uplocal['__show'] = []
	uplocal['__show'].append(name)
	uplocal = None



def _notes(n):
	# __note = {'WHOOPS': 'WHOOPS'}
	stack = inspect.stack()
	o = []
	for level in range(len(stack)-1, n, -1):
		uplocal = stack[level][0].f_locals
		if '__show' in uplocal:
			for k in uplocal['__show']:
				if k in uplocal:
					o.append( (k, uplocal[k]) )
			del uplocal['__show']
		
		if '__note' in uplocal:
			o.extend( uplocal['__note'].items() )
			del uplocal['__note']
		
		del uplocal
	del stack
	o.sort()

	# Delete duplicate values.  This can happen if
	# a variable is noted at two different levels.
	i = 1
	while i < len(o):
		if o[i] == o[i-1]:
			del o[i]
		else:
			i += 1

	return o


def _dumpmem(n):
	logfd.flush()
	if logfd is not sys.stderr:
		sys.stderr.flush()
	sys.stdout.flush()
	for (k, v) in _notes(n+1):
		logfd.write('#NOTE: %s = %s\n' % (k, v))
	logfd.flush()


def _display(prefix, name, text, level):
	global _counter
	global _last
	if compress and _last == (prefix, name, text):
		_counter += 1
		return
	elif _counter > 0:
		logfd.write('#INFO: : preceeding item repeated %d times.\n' % (_counter+1))
		_counter = 0
		_last = ()
	_dumpmem(level+1)
	logfd.write('#%s: %s: %s\n' % (prefix, name, text))
	_last = (prefix, name, text)
	logfd.flush()


def die(s):
	"""Output a fatal error message and terminate."""
	e = 'ERR: %s: %s' % (_name, s)
	exit(1, e)


def warn(s):
	"""Output a non-fatal warning."""
	# __note = {'WHOOPS': 'WHOOPS'}
	_display('WARN', _name, s, 1)


def info(s):
	"""Output useful information."""
	global _q
	_display('INFO', _name, s, 1)


def catch(extext=None):
	"""Call this inside an except statement.
	It will report the exception and any other information it has."""
	type, value, tback = sys.exc_info()
	if extext is None:
		extext = "die.catch: exception caught.\n"
	_dumpmem(1)
	traceback.print_exception(type, value, tback)
	sys.stderr.flush()
	sys.stdout.flush()
	

def catchexit(extext=None, n=1, text=None):
	"""Call this inside an except statement.  It will report
	all information and then exit."""
	type, value, tback = sys.exc_info()
	if extext is None:
		extext = "die.catch: exception caught.\n"
	_dumpmem(1)
	traceback.print_exception(type, value, tback)
	sys.stderr.flush()
	sys.stdout.flush()
	if text is not None:
		sys.stdout.write('%s\n' % text)
		sys.stdout.flush()
		logfd.write('%s\n' % text)
		logfd.flush()
	sys.exit(n)


def dbg(s):
	"""Output debugging information, if debug is nonzero."""
	if debug:
		_display('DBG', _name, s, 1)


def exit(n, text=None):
	"""Exit, after dumping accumulated messages."""
	_dumpmem(1)
	if text is not None:
		sys.stdout.write('%s\n' % text)
		sys.stdout.flush()
		logfd.write('%s\n' % text)
		logfd.flush()
	sys.exit(n)


def get(key):
	nl = _notes(0)
	for (k, v) in nl:
		if k == key:
			return v
	raise KeyError, key



if __name__ == '__main__':
	debug = 1
	info("You should see a debug message next.")
	dbg("This is the debug message.")
	debug = 0
	note("gleep", "oldest note")
	note("foo", "bar")
	note("foo", "fleep")
	note("foo", "foo")
	note("farf", "newest note")
	info("You should not see a debug message next.")
	dbg("This is the debug message you shouldn't see.")
	warn("This is a warning.")
	warn("This is a warning.")
	warn("This is a warning.")
	info("You should have seen three identical warnings just above.")
	die("This is the end.")
