from setuptools import setup, find_packages
import sys, os

version = "0.2.6"

setup(name='UploadView',
      version=version,
      description="a file uploader app",
      long_description="",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Ethan Jucovy',
      author_email='',
      url='http://k0s.org/hg/uploader',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = uploader.factory:factory
      """,
      )
      
