from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='LinguaPlus',
      version=version,
      description="Content actions and plone.app.iterate support for LinguaPlone.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Daniel Holth',
      author_email='daniel.holth@exac.com',
      url='http://python.org/pypi/LinguaPlus',
      license='GPL',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'slc.outdated',
          'Products.LinguaPlone',
          'plone.app.iterate',
          # -*- Extra requirements: -*-
      ],
      test_suite='nose.collector',
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
