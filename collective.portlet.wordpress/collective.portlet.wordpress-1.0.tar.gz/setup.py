from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.portlet.wordpress',
      version=version,
      description="This package provides portlet that lists blog posts from your wordpress blog.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='portlet wordpress',
      author='Vitaliy Podoba',
      author_email='vitaliy@martinschoel.com',
      url='https://svn.plone.org/svn/collective/collective.portlet.wordpress',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'elementtree',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
)