from setuptools import setup, find_packages
import sys, os

version = '0.0.9'

setup(name='rum-policy',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='security,rum,peak.rules',
      author='Alberto Vaverde Gonzalez, Michael Brickenstein',
      author_email='rum-discuss@googlegroups.com',
      url='http://bitbucket.org/brickenstein/rum-policy',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "rum-generic"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
