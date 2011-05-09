#!/usr/bin/env python
version = '1.0.10'
from setuptools import setup
if __name__ == '__main__':
    setup(name='couchdb-python-curl',
          version=version,
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
          install_requires=['pycurl'],
          entry_points={
              'console_scripts': [
                  'couchdb-curl-pinger = couchdbcurl.pinger:main',
                  'couchdb-curl-viewserver = couchdb.view:main',
                  'couchdb-curl-dump = couchdb.tools.dump:main',
                  'couchdb-curl-load = couchdb.tools.load:main',
                  'couchdb-curl-replicate = couchdb.tools.replication_helper:main'
              ]
          }
          )
