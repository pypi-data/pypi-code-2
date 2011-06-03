#!/opt/local/bin/python2.5
# @file paDevs.py
# 	@ingroup test_src
#   @brief List available devices, including device information.
#	@author Phil Burk http://www.softsynth.com

# $Id: paDevs.py 1 2010-04-28 12:51:15Z dale $
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

# *******************************************************************

def printSupportedStandardSampleRates(inputParameters, outputParameters):
	standardSampleRates = [	\
		8000.0, 9600.0, 11025.0, 12000.0, 16000.0, 22050.0, 24000.0, 	\
		32000.0, 44100.0, 48000.0, 88200.0, 96000.0, 192000.0			\
	]

	printCount = 0
	buf = ""
	for i in range(0, len(standardSampleRates)):
		err = pappy.paIsFormatSupported(inputParameters, outputParameters, 	\
										standardSampleRates[i])
		
		if (err == pappy.pyPaFormatIsSupported):
			if (printCount == 0):
				buf += "\t%8.2f" % standardSampleRates[i]
				printCount = 1
			elif (printCount == 4):
				buf += ",\n\t%8.2f" % standardSampleRates[i]
				printCount = 1
			else:
				buf += ", %8.2f" % standardSampleRates[i]
				printCount = printCount + 1
			
	if (not printCount):
		print "None"
	else:
		print buf
		
# *******************************************************************

def main():
	inputParameters = {}
	outputParameters = {}
	
	try:
		pappy.paInitialize()
	
		print "PortAudio version number = %d\nPortAudio version text = '%s'" %	\
			(pappy.paGetVersion(), pappy.paGetVersionText())
	
		numDevices = pappy.paGetDeviceCount();
		if ( numDevices < 0 ):
			print "ERROR: paGetDeviceCount returned 0x%x" % numDevices
			err = numDevices
			raise SystemError
		
		print "Number of devices = %d" % numDevices
			
		for i in range(0, numDevices):
			deviceInfo = pappy.paGetDeviceInfo(i)
			print "--------------------------------------- device #%d" % i 
			
			# Mark global and API specific default devices
			defaultDisplayed = 0
			
			buf = ""
			hostInfo = pappy.paGetHostApiInfo(deviceInfo['hostApi'])
			
			if (i == pappy.paGetDefaultInputDevice()):
				buf += "[ Default Input"
				defaultDisplayed = 1
			elif (i == hostInfo['defaultInputDevice']):
				buf += "[ Default %s Input" % hostInfo['name']
				defaultDisplayed = 1
			
			if (i == pappy.paGetDefaultOutputDevice()):
				if (defaultDisplayed):
					buf += ","
				else:
					buf += "["
				buf += " Default Output"
				defaultDisplayed = 1
			elif (i == hostInfo['defaultOutputDevice']):
				if (defaultDisplayed):
					buf += ","
				else:
					buf += "["
				buf += " Default %s Output" % hostInfo['name']
				defaultDisplayed = 1
			
			if (defaultDisplayed):
				print buf+" ]"
			
			# print device info fields 
			print "Name                        = %s" % deviceInfo['name']
			print "Host API                    = %s" % hostInfo['name']
			print "Max inputs = %d, Max outputs = %d" % (deviceInfo['maxInputChannels'], deviceInfo['maxOutputChannels'])
			
			print "Default low input latency   = %8.3f" % deviceInfo['defaultLowInputLatency']
			print "Default low output latency  = %8.3f" % deviceInfo['defaultLowOutputLatency']
			print "Default high input latency  = %8.3f" % deviceInfo['defaultHighInputLatency']
			print "Default high output latency = %8.3f" % deviceInfo['defaultHighOutputLatency']
			
				# #ifdef WIN32
				# #ifndef PA_NO_ASIO
			# ASIO specific latency information */
			if( hostInfo['type'] == pappy.pyPaASIO ):
				pass
				
				#             long minLatency, maxLatency, preferredLatency, granularity;
				# 
				#             err = PaAsio_GetAvailableLatencyValues( i,
				# 		            &minLatency, &maxLatency, &preferredLatency, &granularity );
				# 
				#             printf( "ASIO minimum buffer size    = %ld\n", minLatency  );
				#             printf( "ASIO maximum buffer size    = %ld\n", maxLatency  );
				#             printf( "ASIO preferred buffer size  = %ld\n", preferredLatency  );
				# 
				#             if( granularity == -1 )
				#                 printf( "ASIO buffer granularity     = power of 2\n" );
				#             else
				#                 printf( "ASIO buffer granularity     = %ld\n", granularity  );
				#         }
				# #endif /* !PA_NO_ASIO */
				# #endif /* WIN32 */
			
			print "Default sample rate         = %8.2f" % deviceInfo['defaultSampleRate']

			# poll for standard sample rates
			inputParameters['device'] = i;
			inputParameters['channelCount'] = deviceInfo['maxInputChannels']
			inputParameters['sampleFormat'] = pappy.pyPaInt16
			inputParameters['suggestedLatency'] = 0
			inputParameters['hostApiSpecificStreamInfo'] = None
			
			outputParameters['device'] = i;
			outputParameters['channelCount'] = deviceInfo['maxOutputChannels']
			outputParameters['sampleFormat'] = pappy.pyPaInt16
			outputParameters['suggestedLatency'] = 0
			outputParameters['hostApiSpecificStreamInfo'] = None
			  
			if (inputParameters['channelCount'] > 0):
				print "Supported standard sample rates\n for half-duplex 16-bit %d channel input = " %	\
				     	inputParameters['channelCount']
				printSupportedStandardSampleRates(inputParameters, None)
			
			if (outputParameters['channelCount'] > 0):
				print "Supported standard sample rates\n for half-duplex 16-bit %d channel output = " %	\
				     	outputParameters['channelCount']
				printSupportedStandardSampleRates(None, outputParameters)
		
			if (inputParameters['channelCount'] > 0 and outputParameters['channelCount'] > 0 ):
				print "Supported standard sample rates\n for full-duplex 16-bit %d channel input, %d channel output = " %	\
				     	(inputParameters['channelCount'], outputParameters['channelCount'])
				printSupportedStandardSampleRates(inputParameters, outputParameters)
		
		pappy.paTerminate()
		print "----------------------------------------------"
    
		return 0
		
	except SystemError:
		pappy.paTerminate()
		sys.stderr.write("An error occured while using the portaudio stream")
		sys.stderr.write("Error number: %d" % err)
		sys.stderr.write("Error message: %s" % pappy.paGetErrorText(err))
		return err
		
sys.exit(main())
	

