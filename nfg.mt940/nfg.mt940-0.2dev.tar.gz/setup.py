from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='nfg.mt940',
      version=version,
      description="Parser for MT940 files",
      long_description="""\
Handles international SWIFT/MT940 format of bank statements""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='swift mt940 banking',
      author='NFG Net Facilities Group BV',
      author_email='support@nfg.nl',
      url='http://www.nfg.nl',
      license='GPLv3',
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
