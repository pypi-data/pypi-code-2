import os
from setuptools import setup, find_packages

version = '0.4.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

desc = read('Products', 'BibfolderFlexibleView', 'README.txt')
changes = read('docs', 'HISTORY.txt')
long_desc = desc + '\n\nChanges\n=======\n\n' + changes

setup(name='Products.BibfolderFlexibleView',
      version=version,
      description="Flexible folder views for CMFBibliographyAT",
      long_description=long_desc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords=(
          'web application server zope zope2 cmf plone bibliography'),
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      url='http://pypi.python.org/pypi/Products.BibfolderFlexibleView',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFBibliographyAT',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      """,
      )
