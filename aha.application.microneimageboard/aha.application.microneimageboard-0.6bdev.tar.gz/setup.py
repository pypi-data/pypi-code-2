from setuptools import setup, find_packages
import sys, os

version = '0.6b'

setup(name='aha.application.microneimageboard',
      version=version,
      description="An image bbs application with twitter authentication.",
      long_description="""\
A image bbs application that needs authenticate via twitter build on the top \
of microne.' .""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='web aha appengine web',
      author='Atsushi Shibata',
      author_email='shibata@webcore.co.jp',
      url='http://coreblog.org/aha',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      py_modules = ['application',],
      packages = [
        'template', 'asset',
      ],
      install_requires = [
          'aha',
          'aha.plugin.microne',
          'aha.plugin.twitteroauth'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
