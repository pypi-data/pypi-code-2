#!/opt/local/bin/python2.5
# @file paTestSine.py
#	@ingroup test_src
#	@brief Play a sine wave for several seconds.
#       @author Dale Cieslak <desizzle@users.sourceforge.net>
#	@author (C program by Ross Bencina <rossb@audiomulch.com>)
#	@author (C program by Phil Burk <philburk@softsynth.com>)
#
# $Id: paTestSine.py 1 2010-04-28 12:51:15Z dale $
# 
# This program uses the PortAudio Portable Audio Library.
# For more information see: http://www.portaudio.com
# Copyright (c) 1999-2000 Ross Bencina and Phil Burk
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
# ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 

# 
# The text above constitutes the entire PortAudio license; however, 
# the PortAudio community also makes the following non-binding requests:
# 
# Any person wishing to distribute modifications to the Software is
# requested to send the modifications to the original developer so that
# they can be incorporated into the canonical version. It is also 
# requested that these non-binding requests be included along with the 
# license above.
# 

import math
import sys

import pappy

gNumSeconds = 5
gSampleRate = 44100
gFramesPerBuffer = 64

gTableSize = 200

def paCallbackWrapper(userData):
	funcdict = {}
	
	def patestCallback(inputBuffer, 
						framesPerBuffer,			\
						timeInfo,					\
						statusFlags):
		out = []
		data = userData['sine']
		for i in range(0, framesPerBuffer):
			out.append(data[userData['left_phase']])
			out.append(data[userData['right_phase']])
			userData['left_phase'] += 1 
			if (userData['left_phase'] >= gTableSize):
				userData['left_phase'] -= gTableSize
			
			userData['right_phase'] += 3 
			if (userData['right_phase'] >= gTableSize):
				userData['right_phase'] -= gTableSize
				 	
		return pappy.pyPaContinue, out
	
	def streamFinished():
		print "Stream Completed: %s\n" % userData['message']
	
	funcdict['streamcallback'] = patestCallback
	funcdict['finishedcallback'] = streamFinished
	return funcdict

# *******************************************************************
def main():
	print "PortAudio Test: output sine wave. SR = %d, BufSize = %d\n" % (gSampleRate, gFramesPerBuffer)
	
	# initialize sinusoidal wavetable
	data = {}
	data['sine'] = []

	for i in range(0, gTableSize):
		data['sine'].append(math.sin((float(i)/float(gTableSize)) * math.pi * 2. ))
   
	data['left_phase'] = 0
	data['right_phase'] = 0

	err = pappy.pyPaNoError
	
	try:
		err = pappy.paInitialize()
		if (not err == pappy.pyPaNoError):
			raise SystemError
		
		outputParameters = {}
		outputParameters['device'] = pappy.paGetDefaultOutputDevice()
		if (outputParameters['device'] == pappy.pyPaNoDevice):
			sys.stderr.write("ERROR: no default output device")
			raise SystemError

		outputParameters['channelCount'] = 2
		outputParameters['sampleFormat'] = pappy.pyPaFloat32
		outputParameters['suggestedLatency'] = pappy.paGetDeviceInfo( outputParameters['device'] )['defaultLowOutputLatency']
		outputParameters['hostApiSpecificStreamInfo'] = None;
	
		stream = None
		pyPaTestCallback = paCallbackWrapper(data)
		(err, stream) = pappy.paOpenStream(None,				\
											outputParameters,	\
											gSampleRate,		\
											gFramesPerBuffer,	\
											pappy.pyPaClipOff,	\
											pyPaTestCallback)
		if (not err == pappy.pyPaNoError):
			raise SystemError									
		
		data['message'] = "No Message"

		err = pappy.paSetStreamFinishedCallback(stream, True)
		if (not err == pappy.pyPaNoError):
			raise SystemError
		
		err = pappy.paStartStream(stream)
		if (not err == pappy.pyPaNoError):
			raise SystemError
		
		print "Play for %d seconds." % gNumSeconds
		pappy.paSleep(gNumSeconds * 1000)
		
		err = pappy.paStopStream(stream)
		if (not err == pappy.pyPaNoError):
			raise SystemError
		
		err = pappy.paCloseStream(stream)
		if (not err == pappy.pyPaNoError):
			raise SystemError
		
		pappy.paTerminate()
		print "Test finished"
	
		return 0
	
	except SystemError:
		paTerminate()
		sys.stderr.write("An error occured while using the portaudio stream")
		sys.stderr.write("Error number: %d" % err)
		sys.stderr.write("Error message: %s" % pappy.paGetErrorText(err))
		return err

sys.exit(main())
