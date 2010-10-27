from setuptools import setup, find_packages
import os

version = '0.9'

setup(name='gomobile.convergence',
      version=version,
      description="Multichannel content discrimination and overrides for Plone CMS",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='mobile',
      author='Mikko Ohtamaa',
      author_email='mikko.ohtamaa@twinapex.com',
      url='http://www.twinapex.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gomobile'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.behavior',
          'plone.directives.form',
          'zope.schema',
          'zope.interface',
          'zope.component',
          'gomobile.mobile',
          '',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-


      [z3c.autoinclude.plugin]
      target = plone        
      """,
      )
