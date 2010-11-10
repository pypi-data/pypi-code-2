from setuptools import setup, find_packages
import os

version = '1.3rc2'

setup(name='Products.InlinePhotoAlbum',
      version=version,
      description="Display an image gallery inside a Plone rich text area",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "TODO.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone gallery inline embed',
      author='Huub Bouma',
      author_email='info@gw20e.com',
      url='http://plone.org/products/InlinePhotoAlbum',
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

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
