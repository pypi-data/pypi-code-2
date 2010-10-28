#!/usr/bin/python

"""When run as a script:
python ~/lib/wavio.py [-g gain] -wavin|-wavout infile outfile
Reads or writes .wav files from any format supported by
gpkimgclass.py .

As a library, allows reading of class gpk_img data from a .WAV
file, and writing class gpk_img to a .WAV file.
"""
import wave
import numpy
import gpkimgclass
from gmisclib import wavio


if __name__ == '__main__':
	import sys
	arglist = sys.argv[1:]
	gain = None
	if len(arglist)==0:
		print __doc__
		sys.exit(1)
	if arglist[0] == '-g':
		arglist.pop(0)
		gain = float(arglist.pop(0))
	if arglist[0] == '-wavin':
		x = wavio.read(arglist[1])
		if gain is not None:
			numpy.multiply(x.d, gain, x.d)
		x.write(arglist[2])
	elif arglist[0] == '-wavout':
		x = gpkimgclass.read(arglist[1])
		rxd = numpy.ravel(x.d)
		mxv = max( rxd[numpy.argmax(rxd)], -rxd[numpy.argmin(rxd)] )
		print "# max=", mxv
		if gain is None:
			gain = 32000.0/mxv
		wavio.write(x, arglist[2], gain)
	else:
		print __doc__
		sys.exit(1)
