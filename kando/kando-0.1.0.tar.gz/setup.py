#!/usr/bin/env python3

import sys
import os
from distutils.core import setup

setup(
    name='kando',
    version='0.1.0',
    author='Niels Serup',
    author_email='ns@metanohi.name',
    url='http://metanohi.name/projects/kando/',
    description='a simple todo list manager',
    long_description=open('README.txt').read(),
    license='Apache License 2.0',
    py_modules=['kando'],
    scripts=['kando'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'License :: DFSG approved',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.1',
        'Environment :: Console',
        'Topic :: Utilities',
        'Topic :: Text Editors',
        ])
