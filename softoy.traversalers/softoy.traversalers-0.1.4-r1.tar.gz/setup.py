# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.1.4-r1'

setup(name='softoy.traversalers',
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
      packages = find_packages(),
      namespace_packages=['softoy',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'zodb3',
      ],
      entry_points="""
      """,
      )
