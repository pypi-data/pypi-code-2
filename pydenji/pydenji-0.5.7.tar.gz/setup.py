#!/usr/bin/env python
from setuptools import setup, find_packages
import sys

# quick hack, will probably do something better later.
requirements = ["configobj", "byteplay==0.2"]
if sys.version_info[1] < 7:
    requirements.append("importlib")

setup(name='pydenji',
      description='Dependency Injection Toolkit',
      # add byteplay as soon as it works.
      version='0.5.7',
      install_requires=requirements,
      long_description=open("README").read(),
      author='Alan Franzoni',
      license='APL 2.0',
      keywords='dependency injection inversion control ioc container',
      author_email='username@franzoni.eu',
      url='http://pypi.python.org/simple/pydenji',
      packages=find_packages(exclude=["test"]),
      setup_requires=["setuptools_hg"],
     )
