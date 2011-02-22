from setuptools import setup, find_packages
import os

version = '0.008'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('docs', 'README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('docs', 'CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )


setup(name='quantumcore.storages',
      version=version,
      description="A collection of storage modules like for file management, metadata and more",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities"
        ],
      keywords='quantumcore storages mongodb metadata assets assetmanagement filesystem files',
      author='Christian Scholz et al',
      author_email='cs@comlounge.net',
      url='http://quantumcore.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quantumcore'],
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
