from setuptools import setup, find_packages
import sys, os

version = '0.3.0'

setup(name='rum-generic',
      version=version,
      description="Generic Functions  Builder from RUM",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='peak.rules',
      author='Alberto Vaverde Gonzalez, Michael Brickenstein',
      author_email='rum-discuss@googlegroups.com',
      url='http://bitbucket.org/brickenstein/rum-generic',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "PEAK-Rules>=0.5a1.dev-r2569",
          "prioritized_methods >= 0.2.1",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
