import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1.1'

longdescription=(
    read('collective/validator/xhtmlStrict/README.txt')+
    '\n' +
    read('collective/validator/xhtmlStrict/HISTORY.txt')
    )

setup(name='collective.validator.xhtmlStrict',
      version=version,
      description="XHTML Strict Validator for collective.validator.base",
      long_description=longdescription,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone Validator XHTMLStrict',
      author='Andrea Cecchi',
      author_email='sviluppoplone@redturtle.net',
      url='https://svn.plone.org/svn/collective/collective.validator.xhtmlStrict',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
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
