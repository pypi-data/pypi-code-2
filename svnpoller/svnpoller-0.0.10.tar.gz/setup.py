# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.0.10'
long_description = \
  open(os.path.join("src","svnpoller","README.txt")).read() + \
  open(os.path.join("TODO.txt")).read()

classifiers = [
   "Development Status :: 4 - Beta",
   "Intended Audience :: System Administrators",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
]

setup(
    name='svnpoller',
    version=version,
    description='polling svn repository and notify by email.',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['subversion','svn','poll','notify'],
    author='Takayuki SHIMIZUKAWA',
    author_email='shimizukawa at gmail.com',
    url='http://bitbucket.org/shimizukawa/svnpoller',
    license='PSL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data = {'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[
       'setuptools',
        # -*- Extra requirements: -*-
    ],
    extras_require=dict(
        test=[
            'Nose',
            'minimock',
        ],
    ),
    test_suite='nose.collector',
    tests_require=['Nose','minimock'],
    entry_points="""
       [console_scripts]
       svnpoller = svnpoller:run
    """,
)

