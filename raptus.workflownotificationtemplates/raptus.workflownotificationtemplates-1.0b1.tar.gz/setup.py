from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='raptus.workflownotificationtemplates',
      version=version,
      description="Provides a configlet to write notification templates ttw",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone notification',
      author='Raptus AG',
      author_email='dev@raptus.com',
      url='http://raptus.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'raptus.workflownotification',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
