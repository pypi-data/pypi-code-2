from setuptools import setup, find_packages
import os

version = '1.0-beta'

setup(name='xdvtheme.sparkling',
      version=version,
      description="An xdv Theme for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone xdv theme skin laplone',
      author='Michael Miller & Mike Duggan',
      author_email='mmiller@laplone.org',
      url='http://laplone.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['xdvtheme'],
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

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
