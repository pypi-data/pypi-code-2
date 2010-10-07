# -*- coding: utf-8 -*-
# setup.py on stereoids
# similar to 'plone_app' ZopeSkel template, but also featuring:
#
# - defines egg version reading from version.txt
# - uses most internal README.txt

from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "CMFPublicator", "version.txt")).read().strip()

setup(name='Products.CMFPublicator',
      version=version,
      description="CMFPublicator provides a METAL mechanism to publish contents in an arbitrary order, inside classic portlets or home boxes.",
      long_description=open(os.path.join("Products", "CMFPublicator", "README.txt")).read().decode('UTF8').encode('ASCII', 'replace') + '\n' +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='layout content editorial selection publicator',
      author='Jean Ferri',
      author_email='jeanrodrigoferri@yahoo.com.br',
      url='http://svn.plone.org/svn/collective/Products.CMFPublicator',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

