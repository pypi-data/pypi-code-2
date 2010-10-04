# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.omelette
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.3'

long_description = (
    read('README.txt') + '\n' +
    read('docs', 'CONFIGURATION-TIPS.txt') + '\n' +
    read('docs', 'CREDITS.txt') + '\n' +
    read('CHANGES.txt') + '\n' +
    read('docs', 'RUNNING-TESTS.txt') + '\n' +
    'DOWNLOAD\n'
    '========\n'
    )

setup(name='collective.salesforce.rsvp',
      version=version,
      description="RSVP/Event registration system integrating the Plone content management system with \
      the Salesforce.com customer relationship management system.",
      long_description=long_description,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='Zope CMF Plone Salesforce.com CRM registration',
      author='David Glick, Groundwire',
      author_email='davidglick@groundwire.org',
      url='http://groups.google.com/group/plonesf',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.salesforce'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'beatbox>=16.0dev',
          'Products.salesforcebaseconnector>=1.2b1',
          'archetypes.schemaextender',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
