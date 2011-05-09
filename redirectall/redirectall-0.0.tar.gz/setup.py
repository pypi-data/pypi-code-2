from setuptools import setup, find_packages
import sys, os

try:
    description = file('README.txt').read()
except IOError: 
    description = ''

version = "0.0"

setup(name='redirectall',
      version=version,
      description="redirect all traffic as moved permanantly",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='jhammel@mozilla.com',
      url='http://k0s.org/hg/redirector',
      license="MPL",
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
      main = redirectall.factory:factory
      """,
      )
      
