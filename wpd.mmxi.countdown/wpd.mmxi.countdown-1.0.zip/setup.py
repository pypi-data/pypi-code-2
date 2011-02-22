# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("wpd", "mmxi", "countdown", "version.txt")).read().strip()

setup(name='wpd.mmxi.countdown',
      version=version,
      description="Countdown portlet for the World Plone Day 2011",
      long_description=open(os.path.join("wpd", "mmxi", "countdown", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone worldploneday wpd countdown portlet',
      author='Simples Consultoria',
      author_email='products@simplesconsultoria.com.br',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['wpd', 'wpd.mmxi'],
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

