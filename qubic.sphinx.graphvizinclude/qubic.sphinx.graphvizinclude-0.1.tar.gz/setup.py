# -*- coding: utf-8 -*-
'''
Created on Jun 18, 2010

@author: nlaurance
'''
__version__ = '0.1'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='qubic.sphinx.graphvizinclude',
      version=__version__,
      description='Sphinx extension: graphviz generation '
                  'of external dot files',
      long_description='\n.. contents::\n\n' + README + '\n\n' +  CHANGES,
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Documentation",
        ],
      keywords='sphinx graphviz',
      author="Nicolas Laurance",
      author_email="nicolas[dot]laurance<at>gmail",
      url="",
      license="MIT GPLv3",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['qubic', 'qubic.sphinx'],
      zip_safe=False,
      tests_require = [],
      install_requires=['sphinx',
                       ],
      #test_suite="repoze.",
      )
