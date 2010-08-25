from setuptools import setup, find_packages
import sys, os

version = '0.9'

setup(name='atompiglet',
      version=version,
      description="AtomPiglet is a library for interacting with Atom Feeds and AtomPub servers.",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='atompub',
      author='Keith Fahlgren',
      author_email='abdelazer@gmail.com',
      url='http://bitbucket.org/gavin/atom-piglet/',
      license='Apache',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      dependency_links = [ 
      ],  
      install_requires=[
          # -*- Extra requirements: -*-
          'lxml>=2.1.2',
          'isodate>=0.3',
          'pytz',
          'friendly_curl>=0.8.2', 
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
