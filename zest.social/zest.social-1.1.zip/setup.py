from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='zest.social',
      version=version,
      description="Zest Social Bookmarking",
      long_description=open("README.txt").read() + "\n" +
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='social bookmarking addthis',
      author='Zest Software',
      author_email='info@zestsoftware.nl',
      url='http://svn.plone.org/svn/collective/zest.social',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zest'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'archetypes.schemaextender',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
