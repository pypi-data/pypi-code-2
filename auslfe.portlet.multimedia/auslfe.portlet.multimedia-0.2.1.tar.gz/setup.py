from setuptools import setup, find_packages
import os

version = '0.2.1'

setup(name='auslfe.portlet.multimedia',
      version=version,
      description="A simple Plone multimedia Portlet with additional optional features",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        ],
      keywords='plone jquery plonegov portlet multimedia image',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturte.net',
      url='http://plone.org/products/auslfe.portlet.multimedia',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['auslfe', 'auslfe.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
