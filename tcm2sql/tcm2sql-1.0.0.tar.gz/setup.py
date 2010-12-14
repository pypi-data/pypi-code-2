# -*- coding: utf-8 -*-
# Copyright (c) 2010 Michael Howitz
# See also LICENSE.txt

import os.path
import setuptools

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()

version = '1.0.0'

setuptools.setup(
    name='tcm2sql',
    version=version,
    description="Tool for generating SQL commands from a tcm static structure diagram (SSD)",
    long_description=(
        '.. contents::' +
        read('README.txt') +
        read('CHANGES.txt')
        ),
    keywords='sql tcm',
    author='Christian Zagrodnick',
    author_email='mail@gocept.com',
    url='http://code.gocept.com',
    license='GPL 2',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        ],
    packages=setuptools.find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    entry_points="""
    [console_scripts]
    tcm2sql = tcm2sql.tcm2sql:main

    """
    )
