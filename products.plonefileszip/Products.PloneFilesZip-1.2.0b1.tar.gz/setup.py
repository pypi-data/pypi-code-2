# -*- coding: utf-8 -*-
# $Id: setup.py 225406 2010-10-27 16:37:53Z glenfant $
from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = _textFromPath('Products', 'PloneFilesZip', 'version.txt')

setup(name='Products.PloneFilesZip',
      version=version,
      description="PloneFilesZip provides a tool that let users download all files from a folder (recursively) in a ZIP archive",
      long_description=(_textFromPath('Products', 'PloneFilesZip', 'README.txt')
                        + '\n\n'
                        + _textFromPath('Products', 'PloneFilesZip', 'CHANGES')),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Plone"
        ],
      keywords='plone files archives',
      author='Gilles Lenfant',
      author_email='gilles.lenfant@alterway.fr',
      url='http://pypi.python.org/pypi/Products.PloneFilesZip',
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
