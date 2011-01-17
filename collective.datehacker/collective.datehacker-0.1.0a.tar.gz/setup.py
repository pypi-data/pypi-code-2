# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '0.1.0a'

setup(name='collective.datehacker',
      version=version,
      description="Add to Plone a view for changing (cheating!) creation and last modification date",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        ],
      keywords='plone plonegov date creation-date modification-date',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://svn.plone.org/svn/collective/collective.datehacker',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
