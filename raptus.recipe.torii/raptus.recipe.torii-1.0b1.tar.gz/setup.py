# -*- coding: utf-8 -*-
"""
This module contains the tool of raptus.recipe.torii
"""
import os
from setuptools import setup, find_packages

version = '1.0b1'

long_description=open("README.txt").read() + "\n" + \
                 open(os.path.join("docs", "HISTORY.txt")).read()
                 
entry_point = 'raptus.recipe.torii:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='raptus.recipe.torii',
      version=version,
      description='buildout recipe for installing torii',
      long_description=long_description,
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: ZODB",
        "Programming Language :: Python",
        ],
      keywords='zope remote prompt zodb',
      author='sriolo',
      author_email='sriolo@raptus.com',
      url='http://svn.plone.org/svn/collective/raptus.recipe.torii',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus', 'raptus.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'raptus.recipe.torii.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
