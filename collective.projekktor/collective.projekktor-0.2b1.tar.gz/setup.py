from setuptools import setup, find_packages
import os

version = '0.2b1'

setup(name='collective.projekktor',
      version=version,
      description="Ploneised version of Projekktor html5 media player.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='html5 fallback flash video audio media widget',
      author='Ryan Northey, Paul Hennell',
      author_email='code@3ca.org.uk',      
      url='http://packages.python.org/collective.projekktor',
      download_url='http://pypi.python.org/pypi/collective.projekktor/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          "Plone >=4.0",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
