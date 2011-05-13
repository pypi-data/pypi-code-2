"""Read and write files in the form
[label]
text
text
text
[label2]
text
text
...

The format is imperfect to the extent that
it does not allow the text to contain things that
look like labels.


When used as a script, it selects regions of such a file
and prints them on the standard output:
Usage: named_block_file.py key1 [key2] <input >output
The sections labelled key1 and key2 will be output in order,
with no separators other than a newline in between.
"""

import g_encode
import re

_label = re.compile(r"""^\[\s*(.+?)\s*\]\s*$""")

_e = g_encode.encoder(notallowed = r']\r\n%')

def _join(lines):
	n = len(lines)
	if n > 0 and lines[n-1] == '\n':
		n -= 1
	return ''.join(lines)


def read(fd):
	inlabel = None
	lines = []
	d = {}
	for l in fd:
		m = _label.match(l)
		if m:
			if inlabel is not None:
				d[inlabel] = _join(lines)
				lines = []
			inlabel = _e.back(m.group(1))
		else:
			lines.append(l)

	if inlabel is not None:
		d[inlabel] = _join(lines)
	return d


def write_key(fd, k):
	fd.writelines('[%s]\n' % _e.fwd(k))

def write_text(fd, t):
	fd.writelines(t)

def write_line(fd, t):
	fd.writelines([t, '\n'])

def write_line_kv(fd, k, v):
	import avio
	fd.writelines([avio.concoct({k: v}), '\n'])

def write(fd, d):
	for (k, v) in d.items():
		write_key(fd, k)
		write_text(fd, v)
		fd.writelines('\n')
	

def test():
	import sys
	write(sys.stdout, read(sys.stdin))

if __name__ == '__main__':
	import sys
	info = read(sys.stdin)
	for k in sys.argv[1:]:
		sys.stdout.writelines(info[k])
