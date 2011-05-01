#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='dse',
      version='2.0.0-BETA3',
      description='DSE - Simplified "bulk" insert/update/delete for Django.',
      author='Thomas Weholt',
      author_email='thomas@weholt.org',
      long_description=open('README.txt').read(),
      packages = ['dse'],
      install_requires = ['django'],
      url = "https://bitbucket.org/weholt/dse2",
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
