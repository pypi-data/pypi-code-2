from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='collective.portlettabber',
      version=version,
      description="A jQuery plugin for Plone layouts that merge portlets together obtaining a single portlet with tabs",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: User Interfaces",
        ],
      keywords='plone plonegov tab portlet jquery',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/collective.portlettabber',
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
