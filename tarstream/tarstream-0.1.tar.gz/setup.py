#!/usr/bin/env python

from distutils.core import setup

setup(name='tarstream',
      version = '0.1',
      url='http://code.google.com/p/python-tarstream/',
      author="Zhigang Wang",
      author_email="zhigang.x.wang@oracle.com",
      description='An incremental approach to extract files from tarfile.',
      long_description = 'This module provides an incremental approach to ' \
          'extract files from tarfile. This allows you to extract a little ' \
          'bit of a file at a time, which means you can report progress as ' \
          'a file extracts.',
      license='MIT License',
      py_modules=['tarstream'])
