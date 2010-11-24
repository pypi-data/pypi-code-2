from setuptools import setup, find_packages
import sys, os

try:
    description = file('README.txt').read()
except:
    description = ''

version = '0.4'

setup(name='martINI',
      version=version,
      description="edit .ini files from the command line",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ini cli',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/martINI',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'genshi'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ini-get = martini.main:get
      ini-set = martini.main:set
      ini-delete = martini.main:delete
      ini-munge = martini.main:munge

      [paste.app_factory]
      main = martini.web:factory
      """,
      )
