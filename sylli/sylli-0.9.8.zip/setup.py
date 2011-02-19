#!/usr/bin/env python

from distutils.core import setup
import sylli
import os

config_dir = sylli.filepath.get_path('config_dir')
long_d = """ Sylli is a universal syllabifier. Developed for Italian, it
can easily be adapted to any language that is claimed to respect the SSP.
Sylli divides timit, strings, files and directories into syllables and provides
other useful functions for syllable analysis"""

setup(name='sylli',
      version=sylli.VERSION,
      description='SSP Syllabifier - Divides words into syllables',
      long_description=long_d,
      author='Iacoponi Luca',
      author_email='jacoponi@gmail.com',
      url='http://sylli.sourceforge.net',
      license="Apache2 License",
      classifiers = [
      'Development Status :: 4 - Beta',
      'Environment :: Console',
      'Environment :: X11 Applications',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: Academic Free License (AFL)',
      'Operating System :: OS Independent',
      'Programming Language :: Python :: 2',
      'Topic :: Text Processing :: Linguistic',
      ],
      keywords=['NLP', 'CL', 'natural language processing',
                'computational linguistics', 'syllable', 'syllabification',
                'italian', 'linguistics', 'phonology', 'syllabifier'],
      packages=['sylli'],
      scripts = ["bin/sylli", "bin/sylli-command"],
      package_data={'sylli': ['config/sonority.txt',
      'config/sonority_ita-etero.txt',
      'config/sonority_ita-etero.txt',
      "htmldocs/*.*",
      "images/sylli.ico"]},
     )