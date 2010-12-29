# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='collective.subrip2html',
      version=version,
      description="A Plone module to add conversion from SRT format to HTML in portal_transforms tool",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Video",
        "Development Status :: 4 - Beta",
        "Topic :: Text Processing :: Markup",
        ],
      keywords='plone srt html transform subrip',
      author='keul',
      author_email='luca@keul.it',
      url='http://svn.plone.org/svn/collective/collective.subrip2html',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pysrt>0.2.3',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
