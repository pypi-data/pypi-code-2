from setuptools import setup, find_packages
import sys, os

version = '0.0'

setup(name='rum-repoze-what',
      version=version,
      description="repoze.what adapters for rum policy",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Alberto Valverde, Michael Brickenstein',
      author_email='brickenstein@mfo.de',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'rum-repoze-what'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
