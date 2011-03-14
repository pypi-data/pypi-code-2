from setuptools import setup, find_packages
import os

version = '0.5'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src', 'gocept', 'thermosnake', 'README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='gocept.thermosnake',
      version=version,
      description="Nagios check script for temperature monitoring using thermosnake hardware",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
        ],
      keywords='nagios thermosnake',
      author='Daniel Havlik',
      author_email='dh@gocept.com',
      url='http://gocept.com',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_data = {},
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
