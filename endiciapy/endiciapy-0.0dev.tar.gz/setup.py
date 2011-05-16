from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='endiciapy',
      version=version,
      description="Python wrapper for Endicia Label Server Application Programming Interface (API)",
      long_description="""\
Python wrapper for Endicia Label Server Application Programming Interface (API)""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='endicia label api',
      author='mauriciosl',
      author_email='mauriciosl@yahoo.com.br',
      url='https://github.com/troolee/endiciapy',
      license='',
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
