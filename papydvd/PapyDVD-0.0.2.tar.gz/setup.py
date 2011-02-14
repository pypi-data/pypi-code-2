# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'repoze.bfg',
    'SQLAlchemy',
    'transaction',
    'repoze.tm2',
    'zope.sqlalchemy',
    'Babel',
    ]

if sys.version_info[:3] < (2,5,0):
    requires.append('pysqlite')

setup(name='PapyDVD',
      version='0.0.2',
      description='Simple Web application for manage a personal database of DVD movies',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: BFG",
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: Italian",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='keul',
      author_email='luca@keul.it',
      url='http://sourceforge.net/projects/papydvd/',
      keywords='web wsgi bfg dvd database',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='papydvd',
      install_requires = requires,
      message_extractors = { '.': [
             ('**.py',   'chameleon_python', None ),
             ('**.pt',   'chameleon_xml', None ),
             ]},
      entry_points = """\
      [paste.app_factory]
      app = papydvd.run:app
      """
      )

