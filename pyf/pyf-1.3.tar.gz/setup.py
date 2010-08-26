from setuptools import setup, find_packages
import sys, os

version = '1.3'

setup(name='pyf',
      version=version,
      description="Pyf is a dataflow library",
      long_description="""\
""",
      classifiers=['Topic :: Software Development :: Libraries :: Python Modules',
                   'Development Status :: 4 - Beta'], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jonathan Schemoul, Florent Aide, Jerome Collette',
      author_email='jonathan.schemoul@gmail.com, florent.aide@gmail.com, collette.jerome@gmail.com',
      url='http://pyfproject.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['pyf'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "pyf.dataflow",
          "pyf.manager",
          "pyf.splitter",
          "pyf.warehouse"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      test_suite = 'nose.collector',
      )
