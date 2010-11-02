# -*- coding: utf-8 -*-
# $Id: setup.py 225796 2010-10-31 17:46:44Z glenfant $
"""The Products.SharkbiteSSOPlugin for PAS/PlonePAS"""

from setuptools import setup, find_packages
import os

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = read('Products', 'SharkbyteSSOPlugin', 'version.txt')

setup(name='Products.SharkbyteSSOPlugin',
      version=version,
      description="SSO Plugin for Zope 2 PAS and PlonePAS",
      long_description=read("README.txt") + "\n\n" + read("docs", "HISTORY.txt"),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Zope2",
          "Topic :: Security"
          ],
      keywords='PAS SSO plugin',
      author='Ben Mason',
      author_email='ben@sharkbyte.co.uk',
      url='http://plone.org/products/single-sign-on-plugin',
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
