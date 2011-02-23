#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='dse',
      version='0.6.0',
      description='DSE - Delayed SQL Executor',
      author='Thomas Weholt',
      author_email='thomas@weholt.org',
      long_description=open('README.txt').read(),
      py_modules = ['dse'],
      install_requires = ('django'),
      #data_files=[('docs', ['dse.html']),],
      url = "https://bitbucket.org/weholt/dse",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database',
          ],
      )