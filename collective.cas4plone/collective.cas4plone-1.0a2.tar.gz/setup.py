from setuptools import setup, find_packages
import sys, os

version = '1.0a2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='collective.cas4plone',
      version=version,
      description='A PAS plugin that authenticates users against a CAS ' \
                  '(Central Authentication Service) server.',
      long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope PAS',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
#      url='',
      license='ZPL',
      packages=find_packages(),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          # Products.PluggableAuthService is a dep, but can't be explicit in Plone 3.
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
