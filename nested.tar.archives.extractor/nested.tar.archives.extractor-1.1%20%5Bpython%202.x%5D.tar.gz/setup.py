#! /usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "Pushpak Dagade (पुष्पक दगड़े)"
__date__   = "$Jul 1, 2011 19:00:00 PM$"

from setuptools import setup
from extractnested import major_version, minor_version

classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: Freeware',
          'Natural Language :: English',
          'Natural Language :: Hindi',          
          'Operating System :: POSIX :: Linux',
          'Topic :: System :: Archiving',
          'Topic :: Utilities',
          ],

long_description = """
What is a nested tar archive?
==============================
It is a tar archive containing other tar archives which may further
contain many more tar archives (and so on...)

So what does this program do?
==============================
It extracts tar archives recursively.
It can extract the following tar archives - 
.tar, .tgz, .tar.gz, .tar.bz2

What's different in this?
==========================
Ordinary extractors normally just extract a tar archive once, ie
they won't extract any other tar archives (if any) that are present
in it. If it has more tar archives and you want to extract them too,
then you have to yourself extract each of these archives. This can be
a real headache if there are many tar archives (and are nested many
levels deep). I have tried to make this thing easy using this tool.

How to access it from terminal?
==========================
You can access it from the terminal using the command -
extractnested.py tar1.tar [tar2.tar ...]
"""

setup(
    name = 'nested.tar.archives.extractor',
    version = '%d.%d' %(major_version, minor_version),
    scripts = ['extractnested.py', 'CHANGELOG'],
    author = 'Pushpak Dagade',
    author_email = 'guanidene@gmail.com',
    url = 'http://guanidene.blogspot.com/2011/06/nested-tar-archives-extractor.html',
    platforms = "Python 2.6 or 2.7.",
    description = 'A command line utility for recursively extracting nested tar archives.',
    long_description = long_description,
    #classifiers = classifiers
    )
