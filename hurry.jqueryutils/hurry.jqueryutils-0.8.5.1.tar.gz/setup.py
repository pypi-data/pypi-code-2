from setuptools import setup, find_packages
import sys
import os

jqueryutils_version = '0.8.5'
version = '0.8.5.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(name='hurry.jqueryutils',
      version=version,
      description="Hurry resource for JQuery-utils",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='http://pypi.python.org/pypi/hurry.jqueryutils',
      license='MIT',
      packages=find_packages('src', exclude=['ez_setup']),
      namespace_packages=['hurry'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'hurry.resource >= 0.10',
          'hurry.jquery',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'hurry.resource.libraries': [
            'jqueryutils = hurry.jqueryutils:jqueryutils_lib',
            ],
      },
     extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
      )
