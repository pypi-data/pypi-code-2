#!/usr/bin/env python

try:
        from setuptools import setup
except ImportError:
        from distutils.core import setup

setup(name='lpthw.web',
      version='1.1',
      description='lpthw.web: a fork of web.py for Learn Python The Hard Way',
      author='Zed A. Shaw',
      author_email='zedshaw@zedshaw.com',
      url='http://learnpythonthehardway.org/',
      packages=['web', 'web.wsgiserver', 'web.contrib'],
      long_description="Locks web.py at a specific version and removes some magic. Thanks to Aaron Swartz for making it originally.",
      license="Public domain",
      platforms=["any"],
     )
