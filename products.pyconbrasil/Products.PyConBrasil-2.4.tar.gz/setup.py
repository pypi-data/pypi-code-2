# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = read("Products", "PyConBrasil", "version.txt").strip()

setup(name='Products.PyConBrasil',
      version=version,
      description="Package for managing papers and the registration process for PyConBrasil.",
      long_description=read("Products", "PyConBrasil", "README.txt") + "\n" +
                       read("docs", "HISTORY.txt"),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2"
        ],
      keywords='pyconbrasil plone zope registration',
      author='APyB - Associacao Python Brasil',
      author_email='contato@python.org.br',
      url='http://svn.plone.org/svn/collective/Products.PyConBrasil/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-,
          'Products.DataGridField <= 1.7',
          'collective.brasil.vocab>0.5',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
