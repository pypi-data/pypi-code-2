from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='ielectric.fab',
      version=version,
      description="Personal fabric file",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGELOG").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://www.fubar.si',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ielectric'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'fabric',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
