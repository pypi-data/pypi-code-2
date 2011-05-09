#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext_modules = [
    Extension(
        'reddit_rank_sort',
        ['reddit_rank_sort.pyx']
    )
]

setup(
    name='reddit_rank',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    author_email="zsp007@gmail.com",
    requires = ['pyrex'],
    version = '0.001',
    description="rebbit rank",
)

