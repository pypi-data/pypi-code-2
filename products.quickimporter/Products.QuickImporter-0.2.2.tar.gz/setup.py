from setuptools import setup, find_packages
import os

version = '0.2.2'

setup(name='Products.QuickImporter',
      version=version,
      description="You can upload .zexp files from your local machine",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Michiharu Sakurai',
      author_email='mojix at mojix.org',
      #maintainer='Marshall Scorcio',
      #maintainer_email='marshall scorcio at gmail com',
      url='http://www.zope.org/Members/mojix/QuickImporter/',
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
      """,
      )
