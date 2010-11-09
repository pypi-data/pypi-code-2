#!/usr/bin/python

##################################################
#       BitLyClient Library
#-------------------------------------------------
#   Copyright:    (c) 2010 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     damjan[at]resume[dot]com
##################################################


__version__ = "$Id: setup.py 760 2010-07-16 15:40:24Z qvasimodo $"

from distutils.core import setup

setup( name = "BitLyClient Library",
       version = '1.0.0',
       py_modules = ['BitLyClient'],
	   description = "This module will help you to cut the long link(s) via web service from the Bit.Ly",
	   author = "Damjan Krstevski",
	   author_email = "damjan@resume.com",
	   license = "GNU (GPL)",
	   keywords = "bit.ly, facebook, twitter, library, python",
	   classifiers = ["Development Status :: 4 - Beta",
					  "License :: OSI Approved :: GNU General Public License (GPL)",
                      "Programming Language :: Python",
                      "Topic :: Software Development :: Libraries :: Python Modules",
                     ],
      )
