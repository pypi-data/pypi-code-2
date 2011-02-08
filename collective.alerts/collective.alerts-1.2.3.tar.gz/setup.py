from setuptools import setup, find_packages
import os

version = '1.2.3'

setup(name='collective.alerts',
      version=version,
      description="Implements Cory LaViska's JQuery Alerts feature for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone jquery alerts',
      author='JC Brand, Cory LaViska',
      author_email='jc@opkode.com',
      url='http://svn.plone.org/svn/collective/collective.alerts',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.js.jqueryui',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
