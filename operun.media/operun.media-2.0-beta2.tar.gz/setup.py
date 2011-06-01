from setuptools import setup, find_packages
import os

version = '2.0-beta2'

setup(name='operun.media',
      version=version,
      description="A product to integrate any type of media to Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Audio Video Media',
      author='operun.de by Stefan Antonelli',
      author_email='info@operun.de',
      url='http://svn.operun.de/svn/operun.media',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['operun'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg
      """,
      paster_plugins = ["ZopeSkel"],
      )
