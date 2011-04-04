# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

setup(name='zopemetadatamaker',
      # py_modules=['zopemetadatamaker',],
      scripts=['src/zopemetadatamaker/zopemetadatamaker',],
      version="0.1.0",
      description="Bulk creation of .metadata files for Zope skins resources",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU General Public License (GPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Framework :: Zope2",
                   "Framework :: Plone",
                   "Topic :: Utilities"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='file zope metadata creator skins',
      author='keul',
      author_email='luca@keul.it',
      url='http://svn.plone.org/svn/collective/zopemetadatamaker',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup', 'examples', 'tests']),
      package_dir = {'zopemetadatamaker':'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

