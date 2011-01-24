# -*- encoding: UTF-8 -*-
import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'cx_Oracle',
    'sqlalchemy'
]

setup(
    name='litex.cxpool',
    version='1.0',
    description='Native Oracle Session Pool implementation for SQLAlchemy',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Database :: Front-Ends"
    ],
    author='Michal Wegrzynek',
    author_email='mwegrzynek@litex.pl',
    url='https://code.launchpad.net/litex.cxpool',
    license='BSD like, see http://repoze.org/license.html',
    keywords='cxpool oracle sessionpool sqlalchemy proxy',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,    
    test_suite='nose.collector',
    install_requires = requires,
    tests_require=['nose']
)
