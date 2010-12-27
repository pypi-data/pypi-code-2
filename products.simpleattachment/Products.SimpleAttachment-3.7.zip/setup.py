from setuptools import setup, find_packages
import os

version = '3.7'

setup(name='Products.SimpleAttachment',
      version=version,
      description="Simple Attachments for Plone",
      long_description=open("README.txt").read() + '\n' + open('docs/HISTORY.txt').read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone attachments RichDocument',
      author='Martin Aspeli',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      extras_require={ 'test': [
          'zope.testing',
          'collective.testcaselayer',
          'Products.RichDocument',
      ]},
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
