from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='pyf.manager',
      version=version,
      description="DataFlow management system (network and path system) for PyF",
      long_description=open("README.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://pyfproject.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyf'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          "pyf.dataflow",
          "pyf.warehouse"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
