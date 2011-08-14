# -*- coding: utf-8 -*-
# $Id: setup.py 1542 2011-04-01 07:13:53Z amelung $
#
# This file is part of ECLecture.
#
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read('Products', 'ECLecture', 'version.txt').strip()
readme  = read('Products', 'ECLecture', 'README.txt')
history = read('Products', 'ECLecture', 'CHANGES.txt')

long_description = readme + '\n\n' + history

setup(name='Products.ECLecture',
      version=version,
      description = "Managing lectures, seminars and other courses.",
      long_description = long_description,

      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords = '',
      author = 'Mario Amelung and Michael Piotrowski',
      author_email = 'mario.amelung@gmx.de and mxp@dynalabs.de',
      url = 'http://plone.org/products/eclecture/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.DataGridField >= 1.6',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
