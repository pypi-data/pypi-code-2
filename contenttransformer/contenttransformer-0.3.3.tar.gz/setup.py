from setuptools import setup, find_packages
import sys, os

version = "0.3.3"

setup(name='contenttransformer',
      version=version,
      description="transform e.g. file data based on type to be served TTW",
      long_description="""
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/contenttransformer',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
        'WebOb',	
        'Paste',
        'PasteScript',
        'docutils',
        'genshi',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = contenttransformer.factory:factory

      [content_transformers]
      Graphviz = contenttransformer.transformers:Graphviz
      ReST = contenttransformer.transformers:RestructuredText
      Genshi = contenttransformer.transformers:GenshiTransformer
      """,
      )
      
