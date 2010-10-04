from setuptools import setup, find_packages
import os

version = '0.4.2'

setup(name='pyjon.versionning',
      version=version,
      description="Versionning system taking Python objects (likely from an ORM like SQL Alchemy) and saving those objects in a repository with synchronisation facility.",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='versionning mercurial sqlalchemy web',
      author='Jonathan Schemoul',
      author_email='jonathan.schemoul@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pyjon'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          "mercurial>=1.2",
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
