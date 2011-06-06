# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("sc", "apyb", "pythonbrasil6", "version.txt")).read().strip()

setup(name='sc.apyb.pythonbrasil6',
      version=version,
      description="Site policy for PythonBrasil[7]",
      long_description=open(os.path.join("sc", "apyb", "pythonbrasil6", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='apyb plone pythonbrasil plone3',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://www.simplesconsultoria.com.br/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sc', 'sc.apyb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.blob==1.5',
          'plone.app.imaging==1.0.5',
          'archetypes.schematuning==1.2',
          'beyondskins.pythonbrasil.site==3.0.0',
          'Products.LinguaPlone==3.0.1',
          'Products.CMFContentPanels==2.6a7',
          'Products.PloneFormGen==1.6.0',
          'Products.CacheSetup==1.2.1',
          'Products.ATGoogleVideo==0.8.2',
          'Products.PlonePopoll==2.7.0-beta2',
          'Products.PyConBrasil==2.4',
          'Products.Maps==2.0.3',
          'sc.social.bookmarks==0.8',
          'collective.easyslider==0.3.1',
          'sc.kupu.objectsupport==1.0',
          'Products.RedirectionTool==1.2.1',
          'collective.captcha==1.4',
          'experimental.contentcreation==1.0rc1',
          'experimental.catalogqueryplan==3.0',
          'experimental.opaquespeedup==1.0',
          'experimental.daterangeindexoptimisations==1.0dev-r77925',
          'Products.contentmigration==2.0.1',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )

