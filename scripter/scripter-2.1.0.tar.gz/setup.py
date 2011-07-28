#!/usr/bin/env python
# Setup script

"""Description:
Setup script for scripter
Copyright (c) 2010 Benjamin Schiller <benjamin.schiller@ucsf.edu>
All rights reserved.
"""

import os, sys
from distutils.core import setup
try: import py2exe
except ImportError: pass
try: import py2app
except ImportError: pass

def main():
	if not float(sys.version[:3])>=2.6:
		sys.stderr.write("CRITICAL: Python version must greater than or equal to 2.6! python 2.7.1 is recommended!\n")
		sys.exit(1)
	setup(name='scripter',
	      version='2.1.0',
	      description="""Intended for automation of tasks on multicore computers
rewrote scripter to use logging module
breaks compatibility with scripter < 2.1.0""",
	      author='Benjamin Schiller',
	      author_email='benjamin.schiller@ucsf.edu',
	      packages = ['scripter'],
	      package_dir = {'scripter': 'src' + os.sep},
	      )
	
if __name__ == '__main__':
	main()
