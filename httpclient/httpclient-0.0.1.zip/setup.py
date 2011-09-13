'''
Created on Aug 14, 2011
@author: guillaume
'''
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(name='httpclient',
      version='0.0.1',
      author="Guillaume Humbert",
      author_email="guillaume.humbert.jp@gmail.com",
      url='https://github.com/guillaume-humbert/httpclient',
      description='A headless HTTP browser.',
      license='GNU General Public License (GPL) v3',
      package_dir = {'': 'src'},
      packages = find_packages('src'),
      test_suite = 'httpclient_test',
      tests_require = 'mockito')