#!/usr/bin/python

##################################################
#   use0mk
#-------------------------------------------------
#   Copyright:    (c) 2010 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     krstevsky[at]gmail[dot]com
##################################################


__version__ = "$Id: setup.py 760 2010-07-16 15:40:24Z qvasimodo $"

from distutils.core import setup

setup( name = "use0mk",
       version = '1.0.0',
       py_modules = ['use0mk'],
	   description = "Library based on 0.mk API Documentation (http://0.mk/api)",
	   author = "Damjan Krstevski",
	   author_email = "krstevsky@gmail.com",
	   license = "GNU (GPL)",
	   keywords = "0.mk",
	   classifiers = ["Development Status :: 4 - Beta",
			"License :: OSI Approved :: GNU General Public License (GPL)",
                      	"Programming Language :: Python",
                      	"Topic :: Software Development :: Libraries :: Python Modules",
                     	],
      )
