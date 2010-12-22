#! /usr/bin/env python

from setuptools import setup

trove_classifiers=[
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Intended Audience :: Developers",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Topic :: Utilities",
    "Topic :: Software Development :: Libraries :: Python Modules",
    ]

setup(name='llbasetools',
      version='0.1',
      description='Commandline llbase utilities.',
      long_description='llsd translator.',
      author='Nathan Wilcox',
      author_email='nejucomo@gmail.com',
      url='http://bitbucket.org/nejucomo/llbasetools',
      license='GNU GPLv3',
      classifiers=trove_classifiers,
      scripts=['scripts/llsdtool.py'],
      requires=['llbase'],
      )
