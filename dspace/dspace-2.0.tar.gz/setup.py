from setuptools import setup, find_packages
import os

version = '2.0'

setup(name='dspace',
      version=version,
      description="A python library for retrieving data from a DSpace repository.",
      long_description=open("README").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY")).read(),
      classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        ],
      keywords='dspace oaipmh sword',
      author='Texas A&M University Library',
      author_email='webmaster@library.tamu.edu',
      url='http://library.tamu.edu',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pyoai>=2.4.2',
          'lxml>=2.3'
      ])
