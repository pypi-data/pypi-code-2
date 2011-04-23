#!/usr/bin/env python
from setuptools import setup, find_packages
import sys

setup(name='pystateful',
      description='State Pattern toolkit',
      version='0.1.0',
      long_description="State Pattern toolkit",
      author='Alan Franzoni',
      license='APL 2.0',
      keywords='state pattern',
      author_email='username@franzoni.eu',
#      url='http://pypi.python.org/simple/pystateful',
      packages=find_packages(exclude=["test"]),
     )
