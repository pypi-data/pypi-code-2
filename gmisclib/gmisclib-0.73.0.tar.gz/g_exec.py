"""Run a Linux command and capture the result.
This module is thread-safe.

Other than the *_raw functions, these functions ignore comments lines
(e.g. ones starting with '#'), and if they see a line beginning with
an error prefix, they raise an L{ExecError} exception.   The default
error prefix is L{ERR}, but you can set it for each call.
Likewise, the default comment prefix is L{COMMENT}, but you can also set
it with the C{comment} argument of any call.

The basic idea is that
	- you start a subprocess.
	- you feed in a bunch of strings (one at a time) to its standard
		input.  (These come from the C{input} argument.
		You need to know, in advance, how much data to feed it.)
		Note that newlines are not added to the C{input} entries,
		so if you want the strings to be lines, they ought to end
		in a newline.
	- then loop over this:
	- if C{perline} is not None, it feeds the subprocess's standard input
		a string, taken from C{perline}.  (Note that newlines are not
		added; you need to include them if you want them, and you
		probably want them.)
	- it produces an output line
	- repeat
	- keep reading until the subprocess closes its standard output.
When C{perline} is empty, the subprocess's standard input is closed.
These functions continue reading the subprocess's output as long
as it keeps producing.

So, you can do this::

	get(None, ['pwd'])  #  "/home/gpk/whatever"
	getall(None, ['ls']) # Yields a listing of your directory
	get(None, ['sum'], input=['wurgle'])  # Same as typing "echo wurgle | sum" to bash.
	getall(None, ['cat'], input=['wurgle\n'], perline=['biffle\n']) == ['wurgle\n', 'biffle\n']
"""

import g_pipe

class ExecError(Exception):
	"""Something went wrong.   The subprocess did not produce
	output when some was expected, or it generated an
	error line (see L{ERR}, C{err} argument).
	Perhaps, some of the input that you supplied could not be used.
	Also, pipe creation might have failed.
	"""

	def __init__(self, *s):
		Exception.__init__(self, *s)



ERR = 'ERR:' #: This is the default for the prefix for error messages from the subprocess.
COMMENT = '#' #: This is the default for the prefix for comments from the subprocess.


def getiter_raw(s, argv, input=None, perline=None, debug=False):
	"""Read a list of lines from a subprocess.

	@note: If input or perline is badly chosen, one can
		produce a locked loop of pipes.  (Locked loops happen when you have
		too much stuff waiting to be processed.)
	@param s: the name of the program to execute.  (Or L{None}, in
		which case, it is taken from C{argv[0]}).
	@type s: C{str} or L{None}
	@param argv: an array of argument to execute.
	@type argv: C{list(str)}
	@param input: strings to feed
		to the subprocess on startup, before the first output is read.
		These are sent to the subprocess's standard input.
	@type input: array, sequence or iterator, containing strings
	@param perline: is a sequence/iterator of strings to feed in, one at a time,
		as the subprocess is producing data.  (These are fed to the subprocess's
		standard input, one after each output line that it produces.)
	@type perline: array, sequence or iterator, containing strings
	@return: a sequence of the lines of output that the program produced.
		(Newlines are not removed.)
	@rtype: a generator of strings.
	@param debug: Should it print some debugging information?
	@type debug: bool
	@raise ExecError: ZZZ
	"""

	if s is None:
		s = argv[0]

	if debug:
		print '#OPENING', s, argv
	wpipe, rpipe = g_pipe.popen2(s, argv)

	if wpipe is None or rpipe is None:
		raise ExecError('Cannot spawn pipe for {%s}' % s, *argv)
	if input is not None:
		if debug:
			for t in input:
				print '#WRITING <%s>' % t
				wpipe.write(t)
		else:
			for t in input:
				wpipe.write(t)

	if perline is None:
		wpipe.close()
		wpipe = None
	else:
		wpipe.flush()
		perline = perline.__iter__()

	while True:
		if wpipe is not None:
			try:
				nxt = perline.next()
				if debug:
					print "#PERLINE: <%s>" % nxt
				wpipe.write(nxt)
				wpipe.flush()
			except StopIteration:
				wpipe.close()
				wpipe = None
				pass
		line = rpipe.readline()
		if debug:
			print '#LINE: {%s}' % line.rstrip('\n')
		if not line:
			break
		yield line
		# Note that this generator could terminate here!

	if wpipe is not None:
		wpipe.close()
		if perline is not None:
			raise ExecError("Unused input: program {%s} terminated before perline ran out of data" % s,
					*argv)
	sts = rpipe.close()
	# if sts is None:
		# sts = 0
	if sts != 0 :
		raise ExecError('spawned command fails with %d from {%s}' % (sts, s), *argv)


def getiter(s, argv, input=None, perline=None, debug=False, err=ERR, comment='#'):
	"""Read a list of lines from a subprocess, after
	dropping junk like comments.  (Comment lines begin with the C{comment}
	argument).
	Raises an exception if the subprocess returns an error line (the beginning
	of an error line is specified in the C{err} argument).

	@note: If input or perline is badly chosen, one can
		produce a locked loop of pipes.  (Locked loops happen when you have
		too much stuff waiting to be processed.)
	@param s: the name of the program to execute.  (Or L{None}, in
		which case, it is taken from C{argv[0]}).
	@type s: C{str} or L{None}
	@param argv: an array of argument to execute.
	@type argv: C{list(str)}
	@param input: strings to feed
		to the subprocess on startup, before the first output is read.
		These are sent to the subprocess's standard input.
	@type input: array, sequence or iterator, containing strings
	@param perline: is a sequence/iterator of strings to feed in, one at a time,
		as the subprocess is producing data.  (These are fed to the subprocess's
		standard input, one after each output line that it produces.)
	@type perline: array, sequence or iterator, containing strings
	@return: a sequence of the lines of output that the program produced.
		(Newlines are not removed.)
	@rtype: a generator of strings.
	@param debug: Should it print some debugging information?
	@type debug: bool
	@raise ExecError: ZZZ
	"""
	for line in getiter_raw(s, argv, input=input, perline=perline, debug=debug):
		if line.startswith(comment):
			continue;
		line = line.rstrip()
		if err and line.startswith(err):
			raise ExecError('%s from {%s}' % (line, s), *argv)
		yield line


def get(s, argv=None, input=None, perline=None, debug=False, err=ERR, comment='#'):
	"""Read a single line from a subprocess, after dropping junk like comments.
	Raises an exception if the subprocess produces an error line (see L{getiter}, L{ERR})
	or no output.  See L{getiter} for arguments.
	@return: the subprocess's first output line (after dropping comment lines).
	@rtype: C{str}
	@raise ExecError: if the subprocess produces no output, or an error line.
	"""
	try:
		return getiter(s, argv, input, perline=perline,
				debug=debug, err=err, comment=comment).next()
	except StopIteration:
		raise ExecError('no output fron {%s}' % s, *argv)


def get_raw(s, argv=None, input=None, perline=False, debug=False):
	"""Read a single line from a subprocess.  (One normally uses this for
	processes that are always supposed to produce a single line of output.)
	See L{getiter_raw} for arguments.
	@return: the subprocess's first output line.
	@rtype: C{str}
	@raise ExecError: if the subprocess produces no output.
	"""
	try:
		return getiter_raw(s, argv, input, perline=perline, debug=debug).next()
	except StopIteration:
		raise ExecError('no output fron {%s}' % s, *argv)


def getlast(s, argv=None, input=None, perline=False, debug=False, err=ERR, comment='#'):
	"""Read the last line from a subprocess, after dropping junk like comments.
	Raises an exception if the subprocess produces an error line (see L{getiter}, L{ERR})
	or no output.   See L{getiter} for arguments.
	@return: the subprocess's first output line (after dropping comment lines).
	@rtype: C{str}
	@raise ExecError: if the subprocess produces no output, or an error line.
	"""
	ok = False
	for q in getiter(s, argv, input, perline=perline,
				debug=debug, err=err, comment=comment):
		ok = True
	if ok:
		return q
	else:
		raise ExecError('no output fron {%s}' % s, *argv)


def getall(s, argv, input=None, perline=None, debug=False, err=ERR, comment='#'):
	"""Read the text lines produced by a subprocess, after dropping junk like comments.
	Raises an exception if the process produces an error line (see L{getiter}, L{ERR}).
	See L{getiter} for arguments.
	@return: the subprocess's first output line (after dropping comment lines).
	@rtype: C{list(str)}
	@raise ExecError: if the process produces an error line.
	"""
	return list(getiter(s, argv, input=input,
					perline=perline, debug=debug,
					err=err, comment=comment
				)
		)



def test():
	inp = ['once\n', 'upon\n', 'a\n', 'time.\n']
	die.note('inp', inp)
	oup = getall(None, ['cat'], input=inp)
	die.note('oup', oup)
	if oup != ["%s" % q for q in oup]:
		die.die('bad cat')
	if get(None, ['sum'], input=['wurgle'])!='02254     1':
		die.die('bad input sum')
	

if __name__ == '__main__':
	import die
	test()
	test()
	print 'OK'
