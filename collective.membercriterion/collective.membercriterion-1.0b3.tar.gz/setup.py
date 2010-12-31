from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='collective.membercriterion',
      version=version,
      description="An ATContentTypes 'Collection' (aka ATTopic) criterion for comparing content to member properties",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone collection topic criterion member property',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.membercriterion',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Plone',
          'Products.Archetypes',
          'Products.ATContentTypes',
          'Products.PluggableAuthService',
          'Products.CMFCore',
          'zope.i18nmessageid',
          'zope.schema',
          'zope.interface',
      ],
      entry_points="""
      """,
      )
