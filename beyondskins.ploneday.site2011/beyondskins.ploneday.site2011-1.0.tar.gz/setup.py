# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("beyondskins", "ploneday", "site2011", "version.txt")).read().strip()

setup(name='beyondskins.ploneday.site2011',
      version=version,
      description="World Plone Day 2011 theme.",
      long_description=open(os.path.join("beyondskins", "ploneday", "site2011", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme skin simples_consultoria',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['beyondskins', 'beyondskins.ploneday'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

