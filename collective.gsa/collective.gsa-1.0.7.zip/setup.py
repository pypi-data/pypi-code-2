from setuptools import setup, find_packages
import os

version = '1.0.7'

setup(name='collective.gsa',
      version=version,
      description="GSA integration for external indexing and searching",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone gsa indexing search',
      author='Matous Hora (Fry-IT Limited)',
      author_email='matous@fry-it.com',
      url='http://pypi.python.org/pypi/collective.gsa',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.indexing',
          'elementtree',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
