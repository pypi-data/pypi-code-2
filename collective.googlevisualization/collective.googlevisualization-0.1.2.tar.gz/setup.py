from setuptools import setup, find_packages
import sys,os

version = '0.1.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read(os.path.join('docs', 'README.txt'))
    + '\n' +
    read(os.path.join('docs', 'CHANGES.txt'))
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='collective.googlevisualization',
      version=version,
      description="Plone integration for Google Visualization API",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages('src',exclude=['ez_setup']),
      namespace_packages=['collective'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.ATContentTypes',
          'five.grok'
          # -*- Extra requirements: -*-
      ],
      entry_points={
      }
      )
