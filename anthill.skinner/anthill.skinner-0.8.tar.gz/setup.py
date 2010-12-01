from setuptools import setup, find_packages
import os

version = '0.8'

setup(name='anthill.skinner',
      version=version,
      description="Skinning for plone made easy",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='skinning theming plone zope',
      author='Simon Pamies',
      author_email='s.pamies@banality.de',
      url='http://www.banality.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anthill'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'anthill.tal.macrorenderer',
          'collective.autopermission',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [distutils.setup_keywords]
      paster_plugins = setuptools.dist:assert_string_list

      [egg_info.writers]
      paster_plugins.txt = setuptools.command.egg_info:write_arg

      [paste.paster_create_template]
      skinner = anthill.skinner.templates.base_skinner_theme:BaseSkinnerTheme
      """,
      )
