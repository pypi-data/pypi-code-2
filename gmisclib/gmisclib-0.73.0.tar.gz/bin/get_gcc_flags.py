#! /usr/bin/python

"""This script computes a good set of compiler flags by running
gcc on many machines, using -march=native, and then collecting
the resulting flags.

It combines them to make a conservative choice that should run
on all the specified machines.
"""



import sys
import subprocess
try:
	from gmisclib import dictops
except ImportError:
	import dictops


OTARGET = '-O3'
OSAFE = '-O2'
MINIPROG = """int main(int argc, char **argv) { return 0;}\n"""
GCC = 'gcc -v -Q %s test.c -o test'
TRANSPORT = ['ssh', '-x', '-o', 'ConnectTimeout=3',
		'-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveInterval=7',
		'-o', 'ServerAliveCountMax=2']

SCRIPT = """
t=/tmp/gccflags$$
trap "rm -rf $t" EXIT
mkdir $t
cd $t >/dev/null 2>&1 || exit 1
cat <<'ENDEND' >test.c
%s
ENDEND
%s
cd /tmp >/dev/null 2>&1
exit 0
"""

def median_down(x):
	tmp = list(sorted(x))
	return tmp[len(x)//2]


def mergeparams(plist):
	tmp = dictops.dict_of_sets()
	for pdict in plist:
		for (k,v) in pdict.items():
			tmp.add(k, v)
	rv = {}
	for (k, vlist) in tmp.items():
		rv[k] = int(median_down(vlist))
		# print 'mergeparams %s=%s -> %s' % (k, vlist, rv[k])
	return rv


def mergeflags(flist):
	n = len(flist)
	tmp = dictops.dict_of_accums()
	for fset in flist:
		for f in fset:
			tmp.add(f, 1)
	rv = set()
	for (k, m) in tmp.items():
		if k.startswith('-mno-'):
			# sys.stderr.write('k=%s\n' % k)
			kyes = '-m' + k[5:]
			if m > 0:
				assert tmp.get(kyes, 0) < n
				rv.add(k)
		else:
			kno = '-mno-' + k[2:]
			if m == n:
				assert tmp.get(kno, 0) == 0
				rv.add(k)
	return rv


def mergetune(tlist):
	tmp = dictops.dict_of_accums()
	for t in tlist:
		if t is not None:
			tmp.add(t, 1)
	nbest = 0
	best = None
	for (k, v) in tmp.items():
		if v > nbest:
			best = k
			nbest = v
	return best


def prmdiff(d1, d2):
	rv = {}
	for (k, v) in d1.items():
		# print 'prmdiff %s=%s vs %s=%s' % (k, v, k, d2.get(k, None))
		if k not in d2 or v!=d2[k]:
			rv[k] = v
	return rv


def transport(mach):
	return TRANSPORT + [mach, 'sh']


class BadMachine(Exception):
	def __init__(self, *s):
		Exception.__init__(self, *s)


def collect_from(mach, flags):
	tmp = SCRIPT % (MINIPROG, GCC % (' '.join(flags)))
	# print 'transport=', transport(mach)
	p = subprocess.Popen(transport(mach), stderr=subprocess.PIPE,
				stdout=open("/dev/null", 'w'),
				stdin=subprocess.PIPE
				)
	# print 'tmp=', tmp
	p.stdin.write(tmp)
	p.stdin.close()
	prms = {}
	op = set()
	oe = set()
	tn = None
	mode = 0
	for l in p.stderr:
		# print 'l=', l.strip()
		if l.startswith('GCC heuristics:'):
			mode = 1
		elif l.startswith('options passed:'):
			mode = 2
		elif l.startswith('options enabled:'):
			mode = 3
		elif l.startswith('Compiler executable checksum:'):
			mode = 0
		if mode:
			tokens = l.strip().split()
			last = None
			for tok in tokens:
				# print 'tok=', tok
				if last == '--param' and '=' in tok:
					k, v = tok.split('=')
					prms[k] = int(v)
				elif tok.startswith('-mtune='):
					tn = tok.split('=')[1]
				elif tok.startswith('-march='):
					pass
				elif tok.startswith('-f'):
					if mode == 2:
						op.add(tok)
					elif mode == 3:
						oe.add(tok)
				elif tok.startswith('-m'):
					if mode == 2:
						op.add(tok)
					elif mode == 3:
						oe.add(tok)
				last = tok
	if p.wait() != 0:
		raise BadMachine
	return (prms, op, oe, tn)


def flagdiff(a, b):
	rv = set()
	for t in a.symmetric_difference(b):
		if t.startswith('-mno-'):
			rv.add(t)
		elif t in a:
			rv.add(t)
		elif t in b:
			rv.add('-mno-' + t[2:])
	return rv


def compute_flaglist(mlist, iflags):
	params = []
	opassed = []
	oenabled = []
	tunes = []
	for m in mlist:
		try:
			tp, top, toe, tune = collect_from(m, iflags + [OTARGET, '-march=native'])
		except BadMachine:
			continue
		params.append(tp)
		opassed.append(top)
		oenabled.append(toe)
		tunes.append(tune)
	# print 'tunes=', tunes
	pset = mergeparams(params)
	opset = mergeflags(opassed)
	oeset = mergeflags(oenabled)
	typtune = mergetune(tunes)

	mp, mop, moe, mtune = collect_from('localhost', iflags + [OSAFE])
	ap = prmdiff(pset, mp)
	
	# rv = iflags + [OSAFE, '-mtune=%s' % typtune]
	rv = iflags + [OSAFE]
	for (k, v) in ap.items():
		rv.extend(['--param', '%s=%s' % (k, v)])
	for p in flagdiff(opset, mop):
		rv.append(p)
	for p in flagdiff(oeset, moe):
		rv.append(p)
	return rv


if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	if len(arglist) > 1 and arglist[0] in ['-m32', '-m64']:
		flags = [arglist.pop(0)]
	else:
		flags = []
	print ' '.join(compute_flaglist(arglist, flags))
