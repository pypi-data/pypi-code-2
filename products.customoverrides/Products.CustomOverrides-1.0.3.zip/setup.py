from setuptools import setup, find_packages
import sys, os

version = '1.0.3'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='Products.CustomOverrides',
      version=version,
      description="Custom CSS and JS injection for Plone",
      long_description=read('README.txt') + "\n" + read('docs','HISTORY.txt'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone custom CSS JS',
      author='Goldmund, Wyldebeast & Wunderliebe',
      author_email='info@gw20e.com',
      url='http://plone.org/products/customoverrides/',
      license='',
      packages=find_packages(exclude=['ez_setup']),
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
