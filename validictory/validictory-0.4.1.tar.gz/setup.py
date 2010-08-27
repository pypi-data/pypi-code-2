#!/usr/bin/env python

from setuptools import setup, find_packages

from validictory import __version__
DESCRIPTION = "general purpose python data validator"
LONG_DESCRIPTION = open('README.rst').read()

CLASSIFIERS = filter(None, map(str.strip,
"""
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines()))

setup(name='validictory',
      version=__version__,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='James Turk',
      author_email='james.p.turk@gmail.com',
      url='http://github.com/sunlightlabs/validictory',
      license="MIT License",
      platforms=["any"],
      packages=find_packages(),
      test_suite="validictory.tests",
     )
