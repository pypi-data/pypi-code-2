#!/usr/bin/env python

from setuptools import setup
setup(name='pyncomb',
      version='1.0.2',
      description='PYthoN COMBinatorics library',
      author='Sebastian Raaphorst',
      author_email='srcoding@gmail.com',
      url='http://www.site.uottawa.ca/~mraap046',
      packages=['pyncomb'],
      long_description="""
          The pyncomb (PYthoN COMBinatorics) library is a collection of
          functions to work with basic combinatorial objects (e.g. permutations,
          subsets, tuples), and provides algorithms for ranking, unranking, and
          iterating over all objects in a specified class.

          1.0.2: Updated import statements to be Python 3 compatible.
          1.0.1: Attempting to fix mysterious bug regarding imports.
          1.0.0: Initial release.
      """,
      classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Mathematics',
        ],
      keywords='mathematics combinatorics permutations combinations subsets',
      license='Apache 2.0'
      )

