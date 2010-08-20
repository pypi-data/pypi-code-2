from setuptools import setup, find_packages
import sys,os

# qunit doesn't appear to have releases with numbers? we make one up
version = '0.5'

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

setup(name='hurry.qunit',
      version=version,
      description="Hurry resource for JQuery Qunit",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Izhar Firdaus / Martijn Faassen',
      author_email='faassen@startifact.com',
      url='http://pypi.python.org/pypi/hurry.qunit',
      license='MIT / GPL',
      packages=find_packages('src',exclude=['ez_setup']),
      namespace_packages=['hurry'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'hurry.resource >= 0.10',
          # -*- Extra requirements: -*-
      ],
      entry_points={
        'hurry.resource.libraries': [
            'qunit = hurry.qunit:qunit_lib',
            ],
      },
     extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
      )
