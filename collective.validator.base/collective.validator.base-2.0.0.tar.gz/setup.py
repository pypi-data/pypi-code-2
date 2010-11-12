import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '2.0.0'

long_description = (
    read('collective/validator/base/README.txt')+
    '\n' +
    read('collective/validator/base/HISTORY.txt')
    )

setup(name='collective.validator.base',
      version=version,
      description="A Plone pages validator",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Validator XHTML CSS',
      author='Andrea Cecchi',
      author_email='andrea.cecchi@redturtle.net',
      url='https://svn.plone.org/svn/collective/collective.validator.base',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
