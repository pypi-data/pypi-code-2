from __future__ import print_function
import os, sys, unittest, tempfile, shlex

def execfile2(filename, _globals=dict(), _locals=dict(), cmd=None, quiet=False):
	"""
	Execute a Python script using execfile().
	In addition to Python execfile() this method can temporary change the argv params.

	This enables you to call an external python script that requires
	command line arguments without leaving current python interpretor.

	* `cmd` can be string with command line arguments or a list or arguments

	The return value is a numeric exit code similar to the one used for command line tools:
	* 0 - if succesfull; this applies if script receives SystemExit with error code 0
	* 1 - if SystemExit does not contain an error code or if other Exception is received.
	* x - the SystemExit error code (if present)
	"""
	_globals['__name__']='__main__'
	saved_argv = sys.argv # we save sys.argv
	if cmd:
		sys.argv=list([filename])
		if isinstance(cmd , list):
			sys.argv.append(cmd)
		else:
			sys.argv.extend(shlex.split(cmd))
	exit_code = 0
	try:
		execfile(filename, _globals, _locals)
	except SystemExit as e:
		if isinstance(e.code , int):
			exit_code = e.code # this could be 0 if you do sys.exit(0)
		else:
			exit_code = 1
	except Exception:
		if not quiet:
			import traceback
			traceback.print_exc(file=sys.stderr)
		exit_code = 1
	finally:
		if cmd:
			sys.argv = saved_argv # we restore sys.argv
	return exit_code

class testExecfile(unittest.TestCase):
	def _exec_py_code(self, code, cmd=None):
		(ftmp, fname_tmp) = tempfile.mkstemp()
		f = open(fname_tmp,"w") # encoding not specified, should use utf-8
		f.write(code)
		f.close()
		exit_code = execfile2(fname_tmp, cmd=cmd, quiet=True)
		os.close(ftmp)
		os.unlink(fname_tmp)
		return exit_code

	def test_normal_execution(self):
		exit_code = self._exec_py_code("")
		self.assertTrue(exit_code==0)

	def test_bad_code(self):
		exit_code = self._exec_py_code("bleah")
		self.assertTrue(exit_code==1)

	def test_sys_exit_0(self):
		exit_code = self._exec_py_code("import sys; sys.exit(0)")
		self.assertTrue(exit_code==0)

	def test_sys_exit_5(self):
		exit_code = self._exec_py_code("import sys; sys.exit(5)")
		self.assertTrue(exit_code==5)

	def test_sys_exit_text(self):
		exit_code = self._exec_py_code("import sys; sys.exit('bleah')")
		self.assertTrue(exit_code==1)

	def test_raised_exception(self):
		exit_code = self._exec_py_code("raise Exception('bleah')")
		self.assertTrue(exit_code==1)

	def test_command_line(self):
		exit_code = self._exec_py_code("import sys\nif len(sys.argv)==2 and sys.argv[1]=='doh!': sys.exit(-1)", cmd="doh!")
		self.assertTrue(exit_code==-1)

if __name__ == "__main__":
	unittest.main()
