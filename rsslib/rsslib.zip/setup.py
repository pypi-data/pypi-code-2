#!/usr/bin/python

##################################################
#       RssLib Library
#-------------------------------------------------
#   Copyright:    (c) 2010 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     krstevsky[at]gmail[dot]com
##################################################


__version__ = "$Id: setup.py 760 2010-07-16 15:40:24Z qvasimodo $"

from distutils.core import setup

setup( name = "RssLib",
       version = '1.0.0.0',
       py_modules = ['RssLib'],
	   description = "This module will help you to read the RSS feeds from some of your favourite websites!",
	   author = "Damjan Krstevski",
	   author_email = "krstevsky@gmail.com",
	   license = "GNU (GPL)",
	   keywords = "rss, library",
	   classifiers = ["Development Status :: 4 - Beta",
					  "Classifier: License :: OSI Approved :: GNU General Public License (GPL)",
                      "Programming Language :: Python",
                      "Topic :: Software Development :: Libraries :: Python Modules",
					  "Classifier: Topic :: Text Processing :: Markup :: XML",
                     ],
      )
