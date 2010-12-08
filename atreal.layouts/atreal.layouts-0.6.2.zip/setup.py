from setuptools import setup, find_packages
import os

version = '0.6.2'

setup(name='atreal.layouts',
      version=version,
      description="Various layouts for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='atreal plone layouts',
      author='atReal',
      author_email='contact@atreal.net',
      url='https://svn.plone.org/svn/collective/atreal.layouts',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['atreal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
