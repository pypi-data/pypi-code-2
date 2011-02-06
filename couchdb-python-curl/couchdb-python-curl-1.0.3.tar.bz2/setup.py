#!/usr/bin/env python

from setuptools import setup
setup(name='couchdb-python-curl',
      version='1.0.3',
      description='CouchDB-python wrapper (using cURL library)',
      author='Alexey Loshkarev',
      author_email='elf2001@gmail.com',
      url='http://code.google.com/p/couchdb-python-curl/',
      packages=['couchdbcurl'],
      license='GPL',
      classifiers=[
          "Development Status :: 5 - Production/Stable", 
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: Database :: Front-Ends",
          ],
      install_requires = ['pycurl'],
      
      )
