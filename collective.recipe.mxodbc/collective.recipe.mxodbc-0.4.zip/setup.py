from setuptools import setup, find_packages

version = '0.4'

setup(name='collective.recipe.mxodbc',
      version=version,
      description="A buildout recipe to install eGenix mx.ODBC and a licence",
      long_description="""\
Notice
======

As of mx.ODBC version 3.1, this recipe is obsolete as the package is now
available as an egg.

Changelog
=========

0.4 (2011-02-04)
----------------

* Update to mx.ODBC version 3.0.4

* Add Python 2.6 version information

""",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "Framework :: Buildout",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Database",
        "Topic :: System :: Installation/Setup",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='build mx.ODBC',
      author='Jarn',
      author_email='info@jarn.com',
      url='http://svn.plone.org/svn/collective/buildout/collective.recipe.mxodbc',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [zc.buildout]
      default = collective.recipe.mxodbc:Recipe
      """,
      )
