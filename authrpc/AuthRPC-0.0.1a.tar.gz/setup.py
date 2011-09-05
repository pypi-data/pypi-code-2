#!/usr/bin/env python
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages
import platform

classifiers = ['Development Status :: 3 - Alpha',
               'Operating System :: OS Independent',
               'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: Internet :: WWW/HTTP :: WSGI']

install_requires = []
exclude = []
extra = {}

if platform.python_version().startswith('2'):
    # we can build server with python 2
    install_requires.append('webob>=1.0.0')

if platform.python_version().startswith('3'):
    # we can't build server with python 3
    exclude.append('AuthRPC.server')
    extra['use_2to3'] = True

setup(name             = 'AuthRPC',
      version          = '0.0.1a',
      packages         = find_packages(exclude=exclude),
      install_requires = install_requires,
      author           = 'Ben Croston',
      author_email     = 'ben@croston.org',
      description      = 'A JSONRPC-like client and server with additions to enable authentication',
      long_description = open('README.txt').read(),
      license          = 'MIT',
      keywords         = 'json, rpc, wsgi, auth',
      url              = 'http://www.wyre-it.co.uk/authrpc/',
      classifiers      = classifiers,
      platforms        = ['Any'],
      test_suite       = 'AuthRPC.tests.suite',
      **extra)

