from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='collective.navroottabs',
      version=version,
      description="Custom portal tabs for Plone folder that are INavigationRoot marked",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        ],
      keywords='plone portal_tabs subsite plonegov',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.net',
      url='http://plone.org/products/collective.navroottabs',
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
