# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.sphinx.includedoc
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'

long_description = (
    read('README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )
setup(name='collective.sphinx.includedoc',
      version=version,
      description="Sphinx extension for including doctests",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        ],
      keywords='zope archetypes sphinx documentation',
      author='Rok Garbas',
      author_email='rok@garbas.si',
      url='http://svn.plone.org/svn/collective/collective.sphinx.includedoc',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.sphinx'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['docutils', 'Sphinx', 'zc.recipe.egg'],
      )
