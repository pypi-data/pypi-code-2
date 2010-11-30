# -*- coding: utf-8 -*-
# $Id: setup.py 9422 2010-11-30 14:56:08Z glenfant $
from setuptools import setup, find_packages
import os

def read(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = read('Products', 'LinguaFace', 'version.txt')

setup(name='Products.LinguaFace',
      version=version,
      description="A product provinding an alternate view and behaviour for LinguaPlone",
      long_description=(read('Products', 'LinguaFace', 'README.txt')
                        + '\n\n'
                        + read('Products', 'LinguaFace', 'CHANGES')),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Plone"
        ],
      keywords='plone linguaplone',
      author='Alter Way Solutions',
      author_email='support@alterway.fr',
      url='http://pypi.python.org/pypi/Products.LinguaFace',
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
