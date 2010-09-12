from setuptools import setup, find_packages
import sys, os

version = '0.8.2'

setup(name='arges',
      version=version,
      description="Simple and multi platform automated testing and tasks execution tool, that can be used straight from the command line.",
      long_description="""\
Simple and multi platform automated testing and tasks execution tool, that can be used straight from the command line.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='automatedtesting,selenium,commandline,automated,testing,multiplatform',
      author='Adri\xc3\xa1n Deccico',
      author_email='deccico@gmail.com',
      url='http://adrian.org.ar',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
