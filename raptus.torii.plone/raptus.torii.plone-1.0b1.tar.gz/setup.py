from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='raptus.torii.plone',
      version=version,
      description="extends raptus.torii",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: ZODB",
        "Programming Language :: Python",
        ],
      keywords='zope remote prompt zodb',
      author='sriolo',
      author_email='sriolo@raptus.com',
      url='http://svn.plone.org/svn/collective/raptus.plone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['raptus', 'raptus.torii'],
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
