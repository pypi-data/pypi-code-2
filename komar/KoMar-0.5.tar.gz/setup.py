#!/usr/bin/env python

#from distutils.core import setup, find_packages
from setuptools import setup, find_packages

import komar


setup(
    name='KoMar',
    version=komar.__version__,
    author="Wojciech 'KosciaK' Pietrzok",
    author_email='kosciak@kosciak.net',
    description='KoMar is simple wiki-markup heavily based on Creole',
    long_description='KoMar is simple wiki-markup heavily based on Creole, check test.wiki file for full syntax description',
    url='http://www.kosciak.net/KoMar/try',
    license='Apache License v2',
    keywords='wiki markup parser',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Environment :: Console",
        "Topic :: Text Processing :: Markup",
        "Topic :: Text Processing :: Markup :: HTML",
        "License :: OSI Approved :: Apache Software License",
    ],
    packages=find_packages(exclude=['ez_setup', 
                                    'tests', 'tests.*'
                                    'examples', 'examples.*']),
    entry_points={
        'console_scripts': [
            'komar = komar:run',
        ],
    },
    #scripts = ['bin/komar'],
)

