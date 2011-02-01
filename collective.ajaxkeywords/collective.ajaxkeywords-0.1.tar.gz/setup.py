from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.ajaxkeywords',
      version=version,
      description="A replacement for the Plone keywords viewlet based on a jquery tag handler.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Dominik Ruf',
      author_email='dominikruf@gmail.com',
      url='https://bitbucket.org/domruf/collective.ajaxkeywords',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.js.jqueryui',
          'five.grok',
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
