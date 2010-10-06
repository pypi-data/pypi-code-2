# -*- coding: utf-8 -*-
"""Installer for this package."""

from setuptools import setup, find_packages

version = '0.5.1'

setup(name='niteoweb.clickbank',
      version=version,
      description="Integrates ClickBank digital products retailer system with Plone for paid memberships.",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone clickbank',
      author='NiteoWeb Ltd.',
      author_email='info@niteoweb.com',
      url='http://svn.plone.org/svn/collective/niteoweb.clickbank',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['niteoweb'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.mocktestcase',
          'collective.recipe.sphinxbuilder',
          'repoze.sphinx.autointerface',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
