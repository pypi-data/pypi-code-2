#!/usr/bin/env python
"""
------------------------------------------------------------
Combino Library

Provides functionality to generate and export 
brute-force.

Usage: python combino.py [options] [arguments]

Opotions:
  -h,  --help				shows this help
  -l,  --length				select length for wordlist generator
  -c,  --charset			select charset for wordlist generator

  -d						show debugging information while running
  -v						show verbose output while running

Examples:
	combino.py -l 5 -c loweralpha
	
This Library is developed and maintained by v3n0m3x
------------------------------------------------------------

"""

__author__ = "v3n0m3x (v3n0m3x@itmix.org)"
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2011/04/09 $"
__copyright__ = "Copyright (c) v3n0m3x"
__license__ = "GPL"

_debug = 0
_verbose = 0

import sys, getopt
import string

class Combino:
	def __init__(self):
		"""main class for parsing input and initializing generations"""
		self.length = 0
		self.charset = ""
		print "    Debug: " + str(bool(_debug))
		print "    Verbose: " + str(bool(_verbose))
		print "Combino class initialized..."
	def set(self, len, set):
		self.length = len
		self.charset = set
		print "    Length: " + str(len)
		print "    Charset: " + set
		print "Input parsed..."
	def combine(self):
		print "Initializing..."
		
def usage():
	"""prints the combino documentation"""
	print __doc__
	
def main(argv):
	try:
		opts, args = getopt.getopt(argv, "h:dv", ["help"])
	except getopt.GetoptError:
		usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			usage()
			sys.exit()
		elif opt == '-d':
			global _debug
			_debug = 1
		elif opt == '-v':
			global _verbose
			_verbose = 1
			
	combino = Combino()
	combino.set(int(args[1]), args[0])
	combino.combine()
	
if __name__ == '__main__':
	main(sys.argv[1:])