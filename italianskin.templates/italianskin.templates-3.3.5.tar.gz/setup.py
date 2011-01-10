import os
from setuptools import setup, find_packages

version = '3.3.5'
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='italianskin.templates',
      version=version,
      description="italianskin XHTML Strict templates for Plone",
      long_description=longdesc,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='davide moro',
      author_email='davide.moro@redomino.com',
      url='http://www.redomino.com/it/labs/progetti/ItalianSkin',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['italianskin'],
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
