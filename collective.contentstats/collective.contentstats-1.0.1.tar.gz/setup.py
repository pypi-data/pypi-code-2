from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='collective.contentstats',
      version=version,
      description="A configlet for Plone showing some content statistics (type/state)",
      long_description=open(os.path.join("collective", "contentstats", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone configlet content reporting',
      author='Raphael Ritz',
      author_email='raphael.ritz@incf.org',
      url='http://svn.plone.org/svn/collective/',
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
      [z3c.autoinclude.plugin]
      target = plone      
      """,
      )
