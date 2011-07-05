from setuptools import setup, find_packages
import os

version = '1.0.0'

setup(name='mobile.htmlprocessing',
      version=version,
      description="Turn arbitary HTML content to mobile browser friendly format",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='html xhtml mobile image processor plone',
      author='mFabrik Research Oy',
      author_email='research@mfabrik.com',
      url='http://webandmobile.mfabrik.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mobile'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'lxml'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
