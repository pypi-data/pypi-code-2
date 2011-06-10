""" Installer
"""
import os
from setuptools import setup, find_packages

name = 'eea.faceted.blue'
path = name.split('.') + ['version.txt']
version = open(os.path.join(*path)).read().strip()

setup(name=name,
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='eea facetednavigation blue theme',
      author='David Batranu',
      author_email='david@eaudeweb.ro',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea', 'eea.faceted'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'eea.facetednavigation',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
