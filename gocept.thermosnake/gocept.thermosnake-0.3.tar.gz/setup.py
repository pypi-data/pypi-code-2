from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='gocept.thermosnake',
      version=version,
      description="Nagios check script for temperature monitoring using thermosnake hardware",
      long_description="requires measuretemp program which can be found on the elektor homepage",
      
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
        ],
      keywords='nagios thermosnake',
      author='Daniel Havlik',
      author_email='dh@gocept.com',
      url='http://gocept.com',
      license='GPL',
      setup_requires=["setuptools_hg"],
      packages=find_packages('src', exclude=['ez_setup']),
      package_data = {
          },
      package_dir = {'':'src'},
      namespace_packages=['gocept'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'nagiosplugin',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            'check_temp_ts = gocept.thermosnake.check_temp_ts:main',],
        }, 
      )
