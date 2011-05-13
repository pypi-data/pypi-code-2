#! /usr/bin/env python

from setuptools import setup

setup(name = 'decotrace',
      description = 'Function/method/class call tracing decorator.',
      author = 'Nathan Wilcox',
      author_email = 'nejucomo@gmail.com',
      version = '0.1.2',
      url = 'https://bitbucket.org/nejucomo/decotrace',
      license = 'GPLv3',

      py_modules = ['decotrace'],

      test_suite = 'test_decotrace',

      setup_requires = ['setuptools_hg'],
      )
