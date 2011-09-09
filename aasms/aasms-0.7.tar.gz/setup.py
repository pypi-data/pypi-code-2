#!/usr/bin/python

# File: setup.py
# Author: Michael Stevens <mstevens@etla.org>
# Copyright (C) 2010

#    This file is part of aasms.
#
#    aasms is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    aasms is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with aasms.  If not, see <http://www.gnu.org/licenses/>.

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(name = "aasms",
      version = "0.7",
      py_modules = ["aasms"],
      description = "aaisp.net SMS interface",
      author = "Michael Stevens",
      author_email = "mstevens@etla.org",
      classifiers = [
        "License :: OSI Approved :: GNU General Public License (GPL)",
		"Intended Audience :: System Administrators",
		"Intended Audience :: Developers",
		"Topic :: Communications :: Telephony",
        ],
      url = "http://github.com/mstevens/aasms",
      scripts = ["send-aa-sms"],
	  packages = find_packages()
      )
