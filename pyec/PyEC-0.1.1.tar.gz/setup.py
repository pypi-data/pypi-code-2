#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages




setup(name='PyEC',
      version='0.1.1',
      description='Evolutionary computation package',
      author='Alan J Lockett',
      install_requires=[
         'django >= 1.2.4',
         'numpy >= 1.5.1',
         'scipy >= 0.8.0'
      ],
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True
)

"""
Note, simpleapi has a requirement on the pstats module, which isn't included in the default Ubuntu
python standard library.  It's a long standing licensing issue, and the workaround is to manually
install python-profiler

sudo apt-get install python-profiler

This is Ubuntu only!!

"""
