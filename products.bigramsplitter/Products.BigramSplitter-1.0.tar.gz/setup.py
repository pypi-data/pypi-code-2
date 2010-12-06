from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='Products.BigramSplitter',
      version=version,
      description="'BigramSplitter' is add-on search product for Plone 3.x. It supports non-English languages, especially south east Asian languages.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Zope Splitter Japanese',
      author='CMScom',
      author_email='terada@cmscom.jp',
      url='http://www.cmscom.jp/',
      source_url='http://code.google.com/p/bigramsplitter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
