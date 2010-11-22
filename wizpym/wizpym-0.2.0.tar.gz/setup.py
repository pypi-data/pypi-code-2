#!/usr/bin/env python

import os
import wizpym
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='wizpym',
      version=wizpym.__version__,
      description='A tool to write Wizard-like apps',
      long_description=read('README'),
      author='David Soulayrol',
      author_email='david.soulayrol@gmail.com',
      url='http://david.soulayrol.name/projects/wizpym/',
      requires=['gobject(>=2.4)', 'gtk(>=2.4)'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: User Interfaces',
        ],
      py_modules=['wizpym'],
      )
