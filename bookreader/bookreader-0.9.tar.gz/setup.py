from setuptools import setup, find_packages
import os

version = '0.9'

setup(name='bookreader',
      version=version,
      description="A Django book reading application that utilizes Djatoka and "
                  "a DSpace repository to present browseable views of scanned "
                  "books.",
      long_description=open("README").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY")).read(),
      classifiers=[
        "Framework :: Django",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Development Status :: 4 - Beta",
        #"Development Status :: 5 - Production/Stable",
        #"Development Status :: 6 - Mature",
        ],
      keywords='djatoka dspace',
      author='Texas A&M University Library',
      author_email='webmaster@library.tamu.edu',
      url='http://library.tamu.edu',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'dspace>=2.0',
      ])
