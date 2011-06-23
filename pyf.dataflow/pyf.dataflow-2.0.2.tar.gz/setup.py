from setuptools import setup, find_packages
import os

version = '2.0.2'

setup(name='pyf.dataflow',
      version=version,
      description="Core DataFlow system of PyF framework",
      long_description=open("README.txt").read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 4 - Beta"
        ],
      keywords='',
      author='',
      author_email='',
      url='http://pyfproject.org',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyf'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyjon.utils',
          'pyf.transport >= 2.0.1',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
