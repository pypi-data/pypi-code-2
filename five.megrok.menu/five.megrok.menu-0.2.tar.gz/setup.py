# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='five.megrok.menu',
      version=version,
      description="Grok support for browser menu in zope 2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2"],
      keywords='',
      author='Jean-François Roche',
      author_email='jfroche@affinitic.be',
      url='http://svn.zope.org/five.megrok.menu/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['five', 'five.megrok'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'five.grok'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
