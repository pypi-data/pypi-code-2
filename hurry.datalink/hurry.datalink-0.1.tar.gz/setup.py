from setuptools import setup, find_packages
import sys,os

version = '0.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read(os.path.join('docs', 'README.txt'))
    + '\n' +
    read(os.path.join('docs', 'CHANGES.txt'))
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='hurry.datalink',
      version=version,
      description="hurry.resource for JQuery Datalink",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Martijn Faassen / Izhar Firdaus',
      author_email='faassen@startifact.com',
      license='MIT',
      packages=find_packages('src',exclude=['ez_setup']),
      namespace_packages=['hurry'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'hurry.resource >= 0.10'
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'hurry.resource.libraries': [
            'datalink = hurry.datalink:datalink_lib',
            ],
      }
      )
