from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='c2.app.shorturl',
      version=version,
      description="Create a Short URL for Plone content",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone zope shorturl',
      author='Manabu TERADA',
      author_email='terada@cmscom.jp',
      url='http://bitbucket.org/cmscom/c2.app.shorturl',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['c2', 'c2.app'],
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
