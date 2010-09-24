#!/usr/bin/env python
"""
====
xodb
====

Development Version
-------------------

The hg `xodb tip`_ can be installed via ``easy_install xodb==dev``.

.. _xodb tip: http://bitbucket.org/pelletier_michel/xodb/get/tip.zip#egg=xodb-dev

"""
from setuptools import setup, find_packages

setup(
  name = "xodb",
  version = "0.2.7",
  packages=find_packages(exclude=['tests.*', 'tests']),

  tests_require=['nose', 'translitcode'],
  test_suite='nose.collector',

  author='Michel Pelletier - Action Without Borders',
  author_email='michel@idealist.org',
  description='experimental xapian object database',
  long_description=__doc__,
  license='MIT License',
  url='http://bitbucket.org/pelletier_michel/xodb/',
      install_requires=[
        'flatland',
        'translitcodec',
        ],
  classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        ],
)
