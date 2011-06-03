# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(name='softoy.widgets',
      version=version,
      description="",
      long_description="""\
        """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Euh Ton-jae',
      author_email='',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'softoy.htmltags',
          'formencode',
      ],
      entry_points="""
      """,
      )
