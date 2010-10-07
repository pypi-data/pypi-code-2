from setuptools import setup, find_packages
import os

JSTREE_VERSION = '1.2.4'
version = '1.2.4'

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

setup(name='hurry.jgrowl',
      version=version,
      description="",
      long_description=long_description,
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Martijn Faassen / Izhar Firdaus',
      author_email='faassen@startifact.com',
      license='MIT',
      packages=find_packages('src'),
      namespace_packages=['hurry'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'hurry.resource >= 0.10',
          'hurry.jquery',
      ],
      entry_points={
       'hurry.resource.libraries': [
        'jgrowl = hurry.jgrowl:jgrowl_lib',
       ],
      }
      )
