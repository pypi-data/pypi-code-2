#!/usr/bin/python

##################################################
#       Google Suggest Grabber
#-------------------------------------------------
#   Copyright:    (c) 2010 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     krstevsky[at]gmail[dot]com
##################################################

__version__ = "$Id: setup.py 760 2010-07-16 15:40:24Z qvasimodo $"

from distutils.core import setup

setup( name = "GoogleSuggest",
       version = '1.0.0',
       py_modules = ['GoogleSuggest'],
	   description = "This module will help you to grab the Google suggestion for some expression.",
	   author = "Damjan Krstevski",
	   author_email = "damjan@resume.com",
	   license = "GNU",
	   keywords = "Google, Google Suggest",
	   classifiers = ["License :: OSI Approved :: GNU General Public License (GPL)",
					  "Programming Language :: Python",
                      "Topic :: Internet :: WWW/HTTP :: Browsers",
                      "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
                      "Topic :: Software Development :: Libraries :: Python Modules",
                      "Topic :: Text Processing :: Filters",
                     ],
      )
