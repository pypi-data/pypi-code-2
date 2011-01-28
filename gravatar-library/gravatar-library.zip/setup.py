#!/usr/bin/python

##################################################
#       GRavatar Library
#-------------------------------------------------
#   Copyright:    (c) 2010 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     krstevsky[at]gmail[dot]com
##################################################


__version__ = "$Id: setup.py 760 2010-07-16 15:40:24Z qvasimodo $"

from distutils.core import setup

setup( name = "GRavatar Library",
       version = '1.0.0',
       py_modules = ['gravatartlib'],
	   description = "This module will help you to communicate with the web services from the GRavatar!",
	   author = "Damjan Krstevski",
	   author_email = "krstevsky@gmail.com",
	   license = "GNU (GPL)",
	   keywords = "gravatar, python",
	   classifiers = ["Development Status :: 4 - Beta",
					  "License :: OSI Approved :: GNU General Public License (GPL)",
                      "Programming Language :: Python",
                      "Topic :: Software Development :: Libraries :: Python Modules",
                     ],
      )
