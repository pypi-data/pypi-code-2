"""This reads HTK feature vectors via the HList program."""


from gmisclib import die
from gmisclib import g_exec
import gpkimgclass
import numpy

def _parse_time(s):
	v, u = s.split()
	if u == 's':
		u = 1.0
	elif u == 'ms':
		u = 1e-3
	elif u == 'us':
		u = 1e-6
	elif u == 'ns':
		u = 1e-9
	elif u == 'ps':
		u = 1e-12
	else:
		die.die('Unrecognized time units: %s' % u)
	return float(v)*u


def read(fname):
	in_hdr = True
	in_os = False
	in_data = False
	os = 0
	ax1 = None
	hdr = {'CRPIX1': 1, 'CRPIX2': 1, 'CRVAL2': 0.0}
	xos = 'x'
	data = None
	hdr['_NAME'] = fname
	for line in g_exec.getiter_raw(None,
					['HList', '-h', '-o', '-i', '1', fname]
					):
		line = line.rstrip()
		if line == ' Observation Structure':
			in_os = True
			in_hdr = False
			continue
		elif in_os and line.startswith(' Samples:'):
			in_os = False
			in_data = True
			data = numpy.zeros((hdr['NAXIS2'], hdr['NAXIS1']))
			continue
		elif line.startswith('----- END'):
			in_data = False

		if in_hdr:
			k, v = line.strip().split(':', 1)
			k = k.strip()
			v = v.strip()
			if k == 'Num Comps':
				hdr['NAXIS1'] = int(v)
			elif k == 'Num Samples':
				hdr['NAXIS2'] = int(v)
			elif k == 'Sample Period':
				hdr['CDELT2'] = _parse_time(v)
			elif k == 'File Format':
				hdr['_FILETYPE'] = v
			else:
				hdr[k] = v
		elif in_os:
			if not line.startswith(' ') and ':' in line:
				xos, tt = line.split(':', 1)
				xos = xos.strip()
				tt = tt.strip()
				os = 0
			else:
				tt = line.strip()
			hdr['TTYPE%d' % (os+1)] = '%s:%s' % (xos, tt)
			os += 1
		elif in_data:
			if ':' in line:
				os = 0
				ax1, line = line.split(':')
				ax1 = int(ax1)
			data[ax1,os] = float(line)
			os += 1
	return gpkimgclass.gpk_img(hdr, data)

if __name__ == '__main__':
	# /home/mace/jyuan/irr_pdur/plp_ip
	import sys
	import pylab
	d = read(sys.argv[1])
	numpy.subtract(d.d, numpy.average(d.d, axis=0), d.d)
	numpy.divide(d.d, numpy.std(d.d, axis=0), d.d)
	pylab.imshow(d.d.transpose(),
			interpolation='nearest', origin='lower',
			aspect = 'normal',
			)
	pylab.show()
