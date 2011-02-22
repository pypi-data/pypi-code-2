#!/usr/bin/python
#  -*- coding=utf-8 -*-
from setuptools import setup, find_packages

setup(
        name = "pynav",
        version = "0.7",
        packages=find_packages(),
        package_data={find_packages()[0]: ['COPYING(ClientForm)']},
        # metadata for upload to PyPI
        author = "sloft",
        author_email = "nomail@example.com",
        description = "Python programmatic web browser to fetch data and test web sites",
        license = "GNU General Public License (GPL)",
        keywords = ["programmatic", "web", "browser"],
        url = "http://bitbucket.org/sloft/pynav/",
        download_url = "http://bitbucket.org/sloft/pynav/downloads/",
	classifiers = [
	"Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
	"Operating System :: OS Independent",
	"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
	"Development Status :: 4 - Beta",
	"Environment :: Console",
	"Topic :: Internet",
	"Intended Audience :: Developers",
	"Topic :: Internet :: WWW/HTTP",
	"Topic :: Internet :: WWW/HTTP :: Browsers",
	"Topic :: Internet :: WWW/HTTP :: Indexing/Search",
	"Topic :: Internet :: WWW/HTTP :: Site Management",
	"Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking",
	"Topic :: Software Development :: Libraries",
	"Topic :: Software Development :: Libraries :: Python Modules",
	],
        long_description = """\
Python programmatic web browser to fetch data and test web sites
________________________________________________________________

Features:

-Post authentication
-User agent support
-Automatic cookie handling
-HTTP Basic Authentication support
-HTTPS support
-Proxy support
-Timeout support
-Reg exp searching
-Links fetching with reg exp filter
-History (pages, posts and responses)
-Save and load history from a file and replay navigation
-Random sleep time beetween pages
-Errors handling
-Content type filters
-Dump forms and generate code
-Check 404 urls
-Check resource datetime
-Handle robots.txt
_______________________________________________________________

Bug reporting and features asking are welcome.
Use the the bug tracker: http://bitbucket.org/sloft/pynav/issues?status=new&status=open
"""
)
