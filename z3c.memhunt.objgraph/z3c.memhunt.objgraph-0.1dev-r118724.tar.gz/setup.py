# -*- coding: utf-8 -*-
"""
This module contains the tool of z3c.memhunt.objgraph

"""
import os
from setuptools import setup, find_packages
from distutils.core import setup, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

libname = 'z3c.memhunt.objgraph'
libloc = libname.split('.')
version = open(os.path.join(*libloc+['version.txt'])).read().strip()


long_description = (
    read('CHANGES.txt')
    + '\n' +
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    )

tests_require=['zope.testing']

setup(name='z3c.memhunt.objgraph',
      version=version,
      description="",
      long_description=long_description,
      namespace_packages=['z3c','z3c.memhunt',],
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords = "zope zope2 zope3 memory objgraph graphviz guppy",
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      author='Daniel Blackburn & Holmes Corporation',
      author_email='danielb@holmescorp.com',
      url="''",
      license = "ZPL 2.1",
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'guppy',
                        'objgraph',
                        ],
      tests_require=tests_require,
#      ext_modules = [Extension("resurrect", ["resurrect.c"]),
#                     Extension("malloc_stats", ["malloc_stats.c"])],
      extras_require=dict(tests=tests_require),
      test_suite = 'z3c.memhunt.objgraph.tests.test_docs.test_suite',
      )



      
