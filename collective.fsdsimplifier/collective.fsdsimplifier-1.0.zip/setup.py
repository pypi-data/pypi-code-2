from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.fsdsimplifier',
      version=version,
      description="Simplifies FacultyStaffDirectory to make it more user friendly.",
      long_description=open("README.txt").read() + "\n" +
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
      [zc3.autoinclude.plugin]
      target = plone

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
