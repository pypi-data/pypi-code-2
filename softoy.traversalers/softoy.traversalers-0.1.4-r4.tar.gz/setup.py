# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import sys, os

version = '0.1.4-r4'

setup(name='softoy.traversalers',
      version=version,
      description="",
      long_description="""\
        """,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Euh Ton-jae',
      author_email='jaeeuh@gmail.com',
      url='',
      license='BSD',
      package_dir={
          'softoy': 'softoy',
          'softoy.traversalers': 'softoy/traversalers',
          'softoy.traversalers.tests': 'softoy/traversalers/tests',
          },
      packages = ['softoy', 'softoy.traversalers', 'softoy.traversalers.tests'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'zodb3',
      ],
      entry_points="""
      """,
      )
