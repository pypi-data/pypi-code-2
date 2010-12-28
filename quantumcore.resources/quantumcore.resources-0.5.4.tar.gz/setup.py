from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.5.4'

long_description = (
    read('docs', 'intro.rst')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='quantumcore.resources',
      version=version,
      description="A resource manager for CSS and JS",
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
      keywords='resources web manager registry css js javascript templates quantumcore',
      author='Christian Scholz',
      author_email='cs@comlounge.net',
      url='http://quantumcore.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quantumcore'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'quantumcore.exceptions',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
