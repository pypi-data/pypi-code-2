from setuptools import setup, find_packages
import os, sys

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

setup(name='sa_mysql_dt',
      version='0.1',
      description="Alternative implementation of DateTime column for MySQL.",
      long_description=long_description,
      classifiers=[], 
      keywords="sqlalchemy MySQL",
      author="Martijn Faassen",
      author_email="faassen@startifact.com",
      url="",
      license="",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'sqlalchemy',
        'MySQL_python',
        ],
      )
