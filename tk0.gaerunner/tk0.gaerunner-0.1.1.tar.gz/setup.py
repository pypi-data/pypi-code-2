# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os, sys

version = '0.1.1'
long_description = \
    open(os.path.join("README.txt")).read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Topic :: Software Development",
]
setup(
    name="tk0.gaerunner",
    version=version,
    description='Python script launcher for Google App Engine (using remote API call)',
    long_description=long_description,
    classifiers=classifiers,
    keywords=['google','app','engine','appengine','gae'],
    author='Takeshi Komiya',
    author_email='i.tkomiya at gmail.com',
    url='',
    license='ASL',
    packages=find_packages('.'),
    package_dir={'': '.'},
    package_data = {'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=[
       'setuptools',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
       [console_scripts]
       gaerunner = tk0.gaerunner:main
    """,
)
