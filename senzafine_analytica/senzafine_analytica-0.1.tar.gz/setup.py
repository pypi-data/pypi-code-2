#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='senzafine_analytica',
      version='0.1',
      description='Senzafine Analytica Service API',
      author='Senzafine.com.br',
      author_email='thiago@senzafine.com.br',
      #url='http://analytica.senzafine.com.br',
      classifiers = ['Topic :: Scientific/Engineering :: Artificial Intelligence',
                    'Topic :: Software Development :: Libraries :: Python Modules',
                    'License :: Freely Distributable'],

      install_requires = ['python-rest-client'],
      package_dir = {'': 'src'},
      packages=find_packages('src'),
      include_package_data = True,
      test_suite = "senzafine.tests.runtests",
     )

