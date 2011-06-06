# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("beyondskins", "pythonbrasil", "site", "version.txt")).read().strip()

setup(name='beyondskins.pythonbrasil.site',
      version=version,
      description="This product is a installable Plone 3 Theme developed by Simples Consultoria for use in Python Brasil [7] Conference web site.",
      long_description=open(os.path.join("beyondskins", "pythonbrasil", "site", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme skin simples_consultoria plone3 brasil apyb',
      author='Simples Consultoria',
      author_email='contato@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['beyondskins', 'beyondskins.pythonbrasil'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'webcouturier.dropdownmenu==2.0',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
