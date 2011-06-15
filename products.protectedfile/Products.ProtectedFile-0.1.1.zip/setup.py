from setuptools import setup, find_packages
import os

version = '0.1.1'

setup(name='Products.ProtectedFile',
      version=version,
      description="'Anonymous users must provide a valid email to download the file.'",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='file',
      author='Jarn & Simula Research Laboratory',
      author_email='info@jarn.com',
      url='http://plone.org/products/protected-file',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
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
