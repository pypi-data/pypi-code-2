from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='vmsutils',
      version=version,
      description="Utilities for virtual machines",
      long_description=open('README.txt').read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Fredo le geek',
      author_email='flg at fredolegeek.org',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'console_scripts': [
            'kvmvalues=vmsutils.kvmvalues:values',
            ],
      },
      )
