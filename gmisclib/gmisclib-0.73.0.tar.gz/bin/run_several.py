#! python

"""This script runs a bunch of processes in parallel.
You tell it what to run on the standard input.
It spawns off a specified number of subprocesses, and hands the jobs
to the subprocesses.

Usage: run_several.py [-v] Ncpu Oom_adjust <list_of_commands >log_of_outputs

Flags: C{-v} means "be more verbose".

C{Ncpu} is the maximum number of cores to devote to running these tasks
(you can enter zero to have it use all the cores of the local machine),
or C{+N} or C{-N} to have it use C{N} more (or less) cores than the machine
has. Further C{x} and C{*} allow you to multiply the number of CPUs by a factor.
(NB: The C{+}, C{-}, C{x}, C{*} forms always leave at least one core running,
no matter what C{N} is or how few cores you have.)
All this can be useful if you want to avoid loading the machine too heavily,
or if you want to boost the loading because your jobs are limited by disk seek time.

C{Oom_adjust} is a number given to Linux's OOM killer.   When
the system starts running out of memory, the OOM killer kills processes.
Positive numbers (e.g. 3) make it more likely that a process will be
killed.   So, if your subtasks are likely to use too much memory
and are not critical, set Oom_adjust positive.

The commands in list_of_commands are just piped into Bash's standard input
one at a time.   Each line is (typically) processed by a different
instance of bash, so don't try any multi-line commands.
The resulting standard outputs and standard errors are kept separate
and each processes' outputs are printed as a lump when it completes.
Stderr from a subprocess comes out as stdout from run_several.py;
various blocks of output are separated by lines with hash marks and
strings of "----" (see write_msgs()).

Note that the processes may finish in any arbitrary order.   The integer
on the stdout and stderr separator lines gives you the (zero-based) line number
in the input file.    Run_several.py returns failure if any of its
subprocesses fail, and it will terminate on the first failure.

Example 1::

	$ echo "pwd" | run_several.py 0 0
	# command 0: pwd
	# stdout 0 ----------------(exited with 0)
	/home/gpk/speechresearch/gmisclib/bin
	# stderr 0 ----------------
	$

Example 2::

	$ { echo uname -m; echo uname -p; echo uname -o;} | run_several.py 0 0
	# command 0: uname -m
	# stdout 0 ----------------(exited with 0)
	x86_64
	# stderr 0 ----------------
	# command 1: uname -p
	# stdout 1 ----------------(exited with 0)
	unknown
	# stderr 1 ----------------
	# command 2: uname -o
	# stdout 2 ----------------(exited with 0)
	GNU/Linux
	# stderr 2 ----------------
	$ 
"""

import sys
import time
import tempfile
import subprocess
from gmisclib import die
from gmisclib import system_load as SL

#: Basic interval to sleep when waiting for the system to become less
#: heavily loaded.
DT = 1.0	# Seconds

def write_msgs(p, exitstatus):
	"""This produces the output.
	"""
	p.x_stderr.seek(0)
	p.x_stdout.seek(0)
	sys.stdout.writelines('# command %d: %s\n' % (p.x_i, p.commandline))
	sys.stdout.writelines('# stdout %d ----------------(exited with %d)\n' % (p.x_i, exitstatus))
	sys.stdout.writelines(p.x_stdout.readlines())
	sys.stdout.writelines('# stderr %d ----------------\n' % p.x_i)
	sys.stdout.writelines(p.x_stderr.readlines())
	sys.stdout.flush()
	p.x_stderr.close()
	p.x_stdout.close()


def get_ncpu():
	n = 0
	for l in open("/proc/cpuinfo", "r"):
		if l.startswith('processor'):
			n += 1
	assert n > 0
	return n


def wait_until_unloaded():
	"""Wait a while until the system becomes less loaded.
	It won't wait forever, though.
	"""
	ncpu = SL.get_ncpu()
	delay = 0
	while delay < 20:
		if SL.get_loadavg() < 2*ncpu and not SL.mem_pressure() < 0.75:
			break
		die.info('# too busy: %.1f/%d %.2f' % (SL.get_loadavg(), ncpu, SL.mem_pressure(ncpu)))
		time.sleep(2*delay*DT)
		delay += 1


def set_oom(pid, ooma):
	trials = 0
	while trials < 6:
		try:
			open('/proc/%d/oom_adj' % pid, 'w').writelines('%d\n' % ooma)
		except IOError, x:
			time.sleep(trials*DT/10.0)
		else:
			trials += 1
			break
	if trials > 3:
		die.warn("Slow start for process %d: writing to /proc/%d/oom_adj: %s" % (pid, pid, x))


def run_processes(fd, np, ooma, verbose):
	running = []
	for (i,line) in enumerate(fd):
		j = 0
		while j < len(running):
			tmp = running[j]
			es = tmp.poll()
			if es is not None:
				if verbose:
					die.info("[End] %d" % es)
				write_msgs(tmp, es)
				if es != 0:
					sys.exit(es)
				del running[j]
			else:
				j += 1
		while len(running) >= np:
			tmp = running.pop(0)
			es = tmp.wait()
			if verbose:
				die.info("[End] %d" % es)
			write_msgs(tmp, es)
			if es != 0:
				sys.exit(es)
		stderr = tempfile.TemporaryFile(prefix="stderr")
		stdout = tempfile.TemporaryFile(prefix="stdout")
		wait_until_unloaded()
		if verbose:
			die.info("[Start] %s" % line.strip())
		p = subprocess.Popen(['bash'], stderr=stderr, stdout=stdout, stdin=subprocess.PIPE)
		p.commandline = line.strip()
		p.x_stderr = stderr
		p.x_stdout = stdout
		p.x_i = i
		set_oom(p.pid, ooma)
		p.stdin.write(line)
		p.stdin.close()
		running.append(p)
		if np>1 and i < np:
			# Don't start the first few processes exactly at the same time.
			# The delays let the memory statistics and system load catch up.
			# This can be important for wait_until_unloaded()
			time.sleep(DT)
	while running:
		tmp = running.pop(0)
		es = tmp.wait()
		if verbose:
			die.info("[End] %d" % es)
		write_msgs(tmp, es)
		if es != 0:
			sys.exit(es)


def parse_NP(s):
	if s.startswith('+') or s.startswith('-'):
		delta = int(s[1:])
		assert -100 <= delta < 1000
		if s.startswith('-'):
			delta = -delta
		return max(1, SL.get_ncpu() + delta)
	elif s.startswith('*') or s.startswith('x'):
		fac = float(s[1:])
		assert 0 <= fac < 10
		return max(1, int(round(SL.get_ncpu()*fac)))
	n = int(s)
	assert 0 <= n < 10000
	if n == 0:
		return SL.get_ncpu()
	return n


if __name__ == '__main__':
	if sys.argv[1] == '-v':
		sys.argv.pop(1)
		verbose = True
	else:
		verbose = False

	NP = parse_NP(sys.argv[1])
	assert 0 < NP < 100
	oom_adj = int(sys.argv[2])
	assert -32 < oom_adj < 32
	run_processes(sys.stdin, NP, oom_adj, verbose)
