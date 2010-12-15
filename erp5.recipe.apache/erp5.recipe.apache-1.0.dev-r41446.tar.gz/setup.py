# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

name = "erp5.recipe.apache"
version = '1.0'

def read(*rnames):
  return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=( read('README.txt')
                   + '\n' +
                   read('CHANGES.txt')
                 )

setup(
  name = name,
  version = version,
  author = 'Łukasz Nowak',
  author_email = 'luke@nexedi.com',
  description = "zc.buildout recipe to create apache instances which servers"
    "Zope content",
  long_description = long_description,
  license = "ZPL 2.1",
  keywords = "apache server buildout",
  classifiers = [
    "License :: OSI Approved :: Zope Public License",
    "Framework :: Buildout",
  ],
  package_dir = {'': 'src'},
  packages = find_packages('src'),
  namespace_packages = ['erp5', 'erp5.recipe'],
  include_package_data = True,
  url='https://svn.erp5.org/repos/public/erp5/trunk/utils/erp5.recipe.apache/',
  install_requires = [
    'setuptools',
    'zc.recipe.egg',
    ],
  entry_points = {'zc.buildout': [
    'default = %s:Zope' % name,
    ]},
  )
