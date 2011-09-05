from setuptools import setup, find_packages
import sys, os

version = '0.6'

setup(name='format_datetime',
      version=version,
      description="Helpers to properly print date and time (strftime replacement).",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='date time international strftime locale format datetime',
      author='Niels Ranosch',
      author_email='ranosch@mfo.de',
      url='https://bitbucket.org/niels_mfo/format_datetime',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
