#!/usr/bin/env python
#
# Copyright 2010 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from distutils.core import Command
from ez_setup import use_setuptools
from glob import glob
from os.path import splitext, basename, join as pjoin, walk
from setuptools import setup, find_packages
from unittest import TextTestRunner, TestLoader
import os
use_setuptools()

# Note to self:
# python setup.py sdist --formats=zip
# To create the zip file

# python setup.py --command-packages=setuptools.command bdist_egg
# To create the egg file

# python setup.py register
# to register with PyPI
#

# create an egg and upload it
# setup.py register bdist_egg upload

# Set this on command line
# DISTUTILS_DEBUG=true
#

NAME = 'mm2notes'
VER = '0.1.1'
RELEASE_FILE = 'RELEASE.rst'
DIR = 'mm2notes'

class TestCommand(Command):
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        testfiles = [ ]
        for t in glob(pjoin(self._dir, NAME, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]])
                )

        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 1)
        t.run(tests)

SETUP = dict(
    name=NAME,
    version=VER,
    description="Convert a FreeMind mind-map (mm) into a meeting notes (html/txt).",
    long_description= """
========
mm2notes
========

Does some XML foo to get meeting notes out of your MM file.
FreeMind is great for taking notes very quickly and is highly recommended.
I sometimes project FreeMind on the overhead projector so that everyone can see the notes I'm taking.
The zoom feature (Alt-Down) is very handy so that it isn't too small.

After the meeting you might check-in the .mm file into a source control program
(if you are into that kind of thing) and then clean up the notes so that it makes more sense and only the salient points are kept.
Then your run something like::

  mm2notes WeeklyMeeting.mm -o WeeklyMeeting.html


To output the notes in HTML, which you can copy and paste to a variety of places.


Screen Shots
------------

In FreeMind your notes will look something like this:

.. image:: http://mm2notes.googlecode.com/svn/trunk/doc/free-mind-shot.png

After running mm2notes on your .mm file the HTML will look like like:

.. image:: http://mm2notes.googlecode.com/svn/trunk/doc/html-shot.png


Features
--------

Attendees can be just a list, at list with e-mails under the person's name (very handy) or a list of cities with the list of people in each city below.

Because FreeMind keeps track of all the times that nodes are created I used that time to organize the meeting minutes.  So even though you may freely jump around adding notes under different people or headings, it'll still organize it by time, so it still makes some sense.

Requirements
------------
* A version of Freemind_.
* Python_.
* ElementTree_ which you'll have automatically if you run Python 2.5 or greater.

`FreeMind <http://freemind.sourceforge.net/wiki/index.php/Main_Page>`_
`Python <http://www.python.org/>`_
`ElementTree <http://effbot.org/zone/element-index.htm>`_

""",
    author='Scott Kirkwood',
    author_email='scott@forusers.com',
    url='http://code.google.com/p/%s' % NAME,
    download_url='http://%s.googlecode.com/files/%s-%s.zip' % (NAME, NAME, VER),
    keywords=['mm', 'FreeMind', 'notes', 'XML', 'text', 'meeting', 'Python'],
    license='Apache 2.0',
    platforms=['POSIX', 'Windows'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: XML',
        'Topic :: Utilities',
    ],
    packages=[NAME],
    scripts=[pjoin('scripts', NAME)],
    cmdclass = { 'test': TestCommand }
)

if __name__ == '__main__':
  setup(**SETUP)
