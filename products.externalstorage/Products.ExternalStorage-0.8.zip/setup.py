from setuptools import setup, find_packages
import os

#version = open(os.path.join("Products", "ExternalStorage", "version.txt")).read().strip()

version = '0.8'

def readfile(infile):
    return open(infile, 'rb').read()

setup(name='Products.ExternalStorage',
      version=version,
      description="An add-on Plone product which provides an extra storage for Archetypes.",
      long_description=(readfile("README.txt") +
        readfile(os.path.join("docs", "HISTORY.txt")) +
        readfile(os.path.join("docs", "AUTHORS.txt"))
        ),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Plone",
        ],
      keywords='Plone Archetypes ExternalStorage',
      maintainer='Dorneles Tremea',
      maintainer_email='deo@plonesolutions.com',
      url='http://plone.org/products/externalstorage',
      license='Custom',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
