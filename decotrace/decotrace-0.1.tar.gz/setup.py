#! /usr/bin/env python

from setuptools import setup

setup(name = 'decotrace',
      description = 'Function/method/class call tracing decorator.',
      author = 'Nathan Wilcox',
      author_email = 'nejucomo@gmail.com',
      version = '0.1',
      url = 'https://bitbucket.org/nejucomo/decotrace',
      license = 'GPLv3',

      py_modules = ['decotrace'],

      setup_requires = ['setuptools_hg'],
      )
