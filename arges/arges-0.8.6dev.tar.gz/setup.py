from setuptools import setup, find_packages
import sys, os

version = '0.8.6dev'

setup(name='arges',
      version=version,
      long_description=open('README.txt').read(),
      description='Simple and multi platform automated testing and tasks execution tool, that can be used straight from the command line.',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Adrian Deccico',
      author_email='deccico@gmail.com',
      url='http://http://code.google.com/p/arges/',
      license='Apache License 2.0',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      scripts=['bin/arges.sh','bin/arges.bat'],
      )
