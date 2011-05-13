"""When used as a script, this reads label files produced by wavesurfer
and prints the result.

Also contains functions that can be used for reading and writing the
label format preferred by Wavesurfer.
"""
import re
import sys
from gmisclib.xwaves_errs import *

_avpat = re.compile('#\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.*)\s*$')

_COMTAG = '_COMMENT'

def read(filename, loose=0):
	"""Read in label (transcription) files produced by wavesurfer.

	Note that leading or trailing spaces in the label are removed.

	@param filename: name of label file or '-' to mean L{sys.stdin}
	@type filename: str
	@param loose: how many minor deviations from the ideal format are allowed
	@type loose: int
	@return: (header, data).
		Data = [(starttime, endtime, label), ...].
	"""
	HUGE = 1e30
	hdr = {}
	if filename == '-':
		fd = sys.stdin
	else:
		try:
			fd = open(filename, "r")
		except IOError, x:
			raise NoSuchFileError, x
	n = 0
	t0last = -HUGE
	t1last = -HUGE
	d = []
	comments = []
	while True:
		n += 1
		l = fd.readline()
		if not l:
			break
		l = l.lstrip().rstrip('\r\n')
		if not l:
			if loose > 0:
				loose -= 1
			else:
				raise BadFileFormatError, 'blank lines prohibited: %s:%d' % (filename, n)
		if l == '#\n':
			continue
		if l.startswith('#'):
			m = _avpat.match(l)
			if m:
				hdr[m.group(1)] = m.group(2).strip()
			else:
				comments.append( l[1:].strip() )
			continue
		a = l.split(None, 2)
		if len(a) == 2 and float(a[0]) and float(a[1]):
			if l[-1] in (' ', '\t'):
				a.append( '' )
			elif loose > 0:
				a.append( '' )
				loose -= 1
			else:
				raise BadFileFormatError, 'label must not be empty: %s:%d' % (filename, n)
		if len(a) == 3:
			try:
				t0 = float(a[0])
				t1 = float(a[1])
			except ValueError:
				raise BadFileFormatError, 'Need <float> <float> before <label> %s:%d' % (filename, n)

			if t0>=t0last and t1>=t1last and t1>=t0:
				d.append( (t0, t1, a[2]) )
				t0last = t0
				t1last = t1
			else:
				raise DataOutOfOrderError, '%s:%d' % (filename, n)

		elif loose > 0:
			loose -= 1
		else:
			raise BadFileFormatError, "Cannot parse line %s:%d" % (filename, n)

	fd = None	# This will close most files, except for sys.stdin
			# which has probably some other reference keeping
			# it open.

	hdr[_COMTAG] = '\n'.join(comments)
	hdr['_NAME'] = filename
	hdr['_FILETYPE'] = 'wavesurfer'
	hdr['NAXIS'] = 2
	hdr['NAXIS2'] = len(d)
	hdr['NAXIS1'] = 3
	hdr['TTYPE1'] = 'start time'
	hdr['TUNIT1'] = 's'
	hdr['TTYPE2'] = 'end time'
	hdr['TUNIT2'] = 's'
	hdr['TTYPE3'] = 'label'

	return (hdr, d)


from xwaves_lab import end_marks, start_stop


def write(fd, header, data):
	"""Write label information to a file.
	Note: Expects data in [(t0, t1, label), ...] form.
	@param fd: where to write
	@param header: header information.
	@type header: dict
	@type fd: file or file-like object
	@param data: a listing of the segments to write to the file.
	@type data: [(segment_start_time, segment_end_time, segment_label), ...]
	"""
	HUGE = 1e30
	d = list(data)
	d.sort()

	fd.write('#wavesurfer_label_gpk\n')
	if _COMTAG in header:
		for x in header[_COMTAG].split('\n'):
			fd.write('# %s\n' % x)
	alist = header.items()
	alist.sort()
	for (a, v) in alist:
		if a != _COMTAG:
			fd.write('# %s = %s\n' % (a, v))
	fd.flush()
	t0last = -HUGE
	t1last = -HUGE
	for (i, (t0, t1, mark)) in enumerate(data):
		if t1 < t0 or t0<t0last or t1<t1last:
			raise DataOutOfOrderError, 'data[%d]: (%s, %s, %s)' % (i, t0, t1, mark)
		fd.write('%.5f %.5f %s\n' % (t0, t1, str(mark).strip()))
	fd.flush()


if __name__ == '__main__':
	hdr, data = read(sys.argv[1])
	for (t0, t1, lbl) in data:
		print t0, t1, lbl
