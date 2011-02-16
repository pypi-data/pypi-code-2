import os
from setuptools import setup, find_packages

version = '1.0'

_here = os.path.dirname(__file__)
def _read(name): return open(os.path.join(_here, name)).read()

setup(name='Products.takeaction',
      version=version,
      description="takeaction, content as actions",
      long_description='\n\n'.join((_read('README.txt'), _read('CHANGES.txt'))),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='content actions translatable',
      author='Jarn',
      author_email='info@jarn.com',
      url='http://plone.org/products/takeaction',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFCore',
          'collective.monkeypatcher',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
