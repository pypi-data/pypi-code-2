#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup

import sys

if sys.version_info < (2, 6):
    print('ERROR: cuevanalinks requires at least Python 2.6 to run.')
    sys.exit(1)

setup(
    name = 'CuevanaLinks',
    version = '0.1',
    description = 'A program to retrieve links of movies or \
                  series from cuevana.tv',
    long_description = open('README.txt').read(), 
    author = u'Martín Gaitán'.encode("UTF-8"),
    author_email = 'gaitan@gmail.com',
    url='https://bitbucket.org/tin_nqn/cuevanalinks',
    packages = ['cuevanalinks',],
    license = 'GNU GENERAL PUBLIC LICENCE v3.0 (see LICENCE.txt)',
    scripts = ['bin/cuevanalinks'],
    install_requires = ['pyquery>=0.5', 'plac>=0.8'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],

)
