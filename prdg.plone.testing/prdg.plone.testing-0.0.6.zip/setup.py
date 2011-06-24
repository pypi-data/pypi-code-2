from setuptools import setup, find_packages
import os

version = '0.0.6'

def file_to_str(filename):
    return open(filename).read()
    
TXT_FILES = ('README.txt', 'TODO.txt', 'HISTORY.txt')

setup(name='prdg.plone.testing',
      version=version,
      description="Provide useful base classes for testing in Plone.",
      long_description='\n'.join(file_to_str(f) for f in TXT_FILES),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone testing TestCase',
      author='Rafael Oliveira',
      author_email='rafaelbco@gmail.com',
      url='http://code.google.com/p/prdg-python/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['prdg'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'prdg.zope.permissions>=0.0.1,<=0.0.99',
          'prdg.util>=0.0.1,<=0.0.99',
          'prdg.plone.util>=0.0.6,<=0.0.99',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
