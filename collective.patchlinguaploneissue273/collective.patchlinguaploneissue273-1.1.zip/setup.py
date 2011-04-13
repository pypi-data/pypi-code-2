from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='collective.patchlinguaploneissue273',
      version=version,
      description="Try to fix http://plone.org/products/linguaplone/issues/273",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='yboussard',
      author_email='youenn.boussard@alterway.fr',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'collective.monkeypatcher'
      ],
      entry_points="""
      # -*- Entry points: -*-

      
      """,
      
      )
