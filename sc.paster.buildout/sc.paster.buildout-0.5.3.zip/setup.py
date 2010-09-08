# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.5.3'

setup(name='sc.paster.buildout',
      version=version,
      description="Simples Consultoria's buildout skeleton for Plone portals.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone development simples_consultoria',
      author='Erico Andrei',
      author_email='erico@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.paster'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'ZopeSkel'
      ],
      tests_require=['zope.testing', 'zc.buildout', 'Cheetah', 'PasteScript','ZopeSkel'],
      test_suite='sc.paster.buildout.tests.test_templates.test_suite',
      entry_points="""
        [paste.paster_create_template]
        portal_buildout = sc.paster.buildout:Buildout
      """,
      )
