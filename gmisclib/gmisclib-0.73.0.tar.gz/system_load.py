import os
import re
import die

def load_avg():
	return float(open("/proc/loadavg", "r").read().strip().split()[0])

def mem_pressure(verbose=False):
	"""@rtype: L{float}
	@return: Big (>1) when the system is really hurting for memory.  Small (<0.5) when things are going well.
		Also, by way of the amount of dirty memory, it indirectly looks at the rate of writing to the disk.
	"""
	SWAPFAC = 1.0
	x = {}
	for l in open("/proc/meminfo", "r"):
		kvu = l.strip().split()
		if len(kvu) > 1:
			x[kvu[0].strip().rstrip(':')] = float(kvu[1])
	swap = SWAPFAC*(x['SwapTotal']-x['SwapFree'])/x['MemTotal']
	active = x['Active'] / x['MemTotal']
	dirty = 10 * x['Dirty'] / x['MemTotal']
	if verbose:
		die.info("mem_pressure: sw=%.2f ac=%.2f d=%.2f" % (swap, active, dirty))
	return swap + active + dirty


_ncpu = None
def ncpu():
	global _ncpu
	if _ncpu is not None:
		return _ncpu
	n = 0
	for l in open("/proc/cpuinfo", "r"):
		if l.startswith('processor'):
			n += 1
	assert n > 0
	_ncpu = n
	return n

get_ncpu = ncpu
get_loadavg = load_avg

# print mem_pressure()
# print get_loadavg()


PROC = '/proc'

class pstat(object):
	_spat = re.compile(r'(\d+) \((.*)\) ([A-Z]) ([0-9]+) ([0-9 -]+)')
	_map = { 'minflt': 5, 'cminflt': 6, 'majflt': 7, 'cmajflt': 8,
			'utime': 9, 'stime': 10, 'cutime': 11, 'cstime': 12,
			'priority': 13, 'nice': 14, 'num_threads': 15, 
			'vsize': 18, 'rss': 19, 'rsslim': 20
			}


	def __init__(self, pid):
		self.pid = pid
		fp = open(os.path.join(PROC, str(pid), 'stat'), 'r')
		self.uid = os.fstat(fp.fileno()).st_uid
		s = fp.read()
		m = self._spat.match(s)
		if not m:
			raise ValueError, "/proc/pid/stat doesn't match pattern: %s" % s
		self.comm = m.group(2)
		self.state = m.group(3)
		self.ppid = int(m.group(4))
		self._more = m.group(5).split()

	def __getattr__(self, name):
		return int(self._more[self._map[name]])



def load_now(my_weight=1, other_weight=2, d_weight=0.5, ignore=None, verbose=False):
	me = os.getuid()
	mypid = os.getpid()
	myload = 0
	oload = 0
	kload = 0
	dload = 0
	for d in os.listdir(PROC):
		try:
			pid = int(d)
		except ValueError:
			continue
		if pid == mypid:
			continue
		try:
			fields = pstat(pid)
		except (ValueError, IOError):
			continue
		if ignore is not None and ignore(pid, fields.ppid, fields.comm):
			continue
		if fields.state in "RD":
			if verbose:
				die.info("pid=%d proc=%s %s" % (fields.pid, fields.comm, fields.state))
			if fields.uid == me:
				myload += 1
			elif fields.uid == 0:	# Kernel
				kload += 1
			else:
				oload += 1
			if fields.state == "D":
				dload += 1

	load = float(myload*my_weight + oload*other_weight + dload*d_weight)
	load += kload * float((myload+1)*my_weight + oload*other_weight) / float(myload+1+oload)
	return load


def niceness():
	ni = pstat(os.getpid()).nice
	return float(ni-9.5)/19.0


if __name__ == '__main__':
	print 'ncpu=', ncpu()
	print 'niceness=', niceness()
	for i in range(5):
		print 'load_now=', load_now(verbose=True), load_now(1,0,0), load_now(0,1,0), load_now(0,0,1)
	print 'mem_pressure', mem_pressure(verbose=True)
