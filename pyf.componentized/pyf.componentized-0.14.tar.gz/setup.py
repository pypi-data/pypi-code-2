from setuptools import setup, find_packages
import sys, os

version = '0.14'

setup(name='pyf.componentized',
      version=version,
      description="Component system for flow based programming with XML configuration system.",
      long_description="""\
This package provides component plugins architecture
for flow-based programming using PyF framework.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='flow pyf zflow programming plugins components',
      author='htaieb',
      author_email='he.taieb@gmail.com',
      url='http://pyfproject.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['pyf'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "pyf >= 1.0dev",
          "pyf.dataflow >= 1.1dev",
          "pyf.manager >= 1.1dev",
          "pyjon.utils",
      ],
      test_suite='nose.collector',
      entry_points="""
      # -*- Entry points: -*-
      [pyf.components.joiners]
      linear = pyf.componentized.builtins.joiners:LinearJoiner
      sequence = pyf.componentized.builtins.joiners:SequencialJoiner
      zip = pyf.componentized.builtins.joiners:ZipJoiner
      orderedkey = pyf.componentized.builtins.joiners:OrderedKeyJoiner
      orderedkeymerge = pyf.componentized.builtins.joiners:OrderedKeyMerger
      """,
      )
