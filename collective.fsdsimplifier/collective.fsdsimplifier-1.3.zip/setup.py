from setuptools import setup, find_packages
import os

version = open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'collective', 'fsdsimplifier', 'version.txt')).read().strip()

setup(name='collective.fsdsimplifier',
      version=version,
      description="Simplifies FacultyStaffDirectory (FSD) for the end-user.",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone facultystaffdirectory',
      author='Heather Wozniak',
      author_email='heather@laplone.org',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.FacultyStaffDirectory',
          'archetypes.schemaextender',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
