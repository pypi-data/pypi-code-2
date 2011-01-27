#!/usr/bin/env python

import os
from setuptools import setup, find_packages

ROOT = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(ROOT, 'README.txt')).read()

setup(
    name = 'RobotDriver',
    version = '0.2.3',
    description = 'RobotFramework support for Bitten',
    long_description = README,
    author = 'Xie Yanbo',
    author_email = 'xieyanbo@gmail.com',
    license = 'New BSD',
    packages = find_packages(),
    package_data = {
        'robotdriver': ['templates/*.html'],
    },
    entry_points = {
        'trac.plugins': [
            'robotdriver.robot = robotdriver.robot',
            ],
        'bitten.recipe_commands': [
            'http://bitbucket.org/xyb/robotdriver#robot = '
            'robotdriver.robot:robot',
            ],
    },
    zip_safe = False,
    url = 'http://bitbucket.org/xyb/robotdriver',
    keywords = 'trac,bitten,robotframework,pybot,test',
    install_requires = [
        'trac>=0.12',
        'bitten>=0.6b3',
        ],
    platforms = ['Linux', 'Unix', 'Windows', 'MacOS X'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Framework :: Trac',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
    ],
)
