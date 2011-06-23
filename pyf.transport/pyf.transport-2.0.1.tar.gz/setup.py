from setuptools import setup, find_packages
import os

version = '2.0.1'

setup(name='pyf.transport',
      version=version,
      description="DataFlow transport (packets) system for PyF framework",
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
          "pyjon.utils",
          "python-dateutil",
          "pyf.splitter",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
