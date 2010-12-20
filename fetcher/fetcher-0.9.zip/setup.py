#!/usr/bin/env python
#coding=utf-8

from setuptools import setup, find_packages

setup(
    name = "fetcher",
    version = "0.9",
    packages = find_packages(),

    install_requires = ['chardet'],

    # metadata for upload to PyPI
    author = "Mutang(牧唐)",
    author_email = "xlty.0512@gmail.com",
    description = "simple python fetcher",
    license = "New BSD License",
    keywords = "python fetcher spider charset",
    url = "http://code.taobao.org/trac/fetcher",
    test_suite = "tests.fetcher_tests.test_all",
    dependency_links = [
        "http://code.taobao.org/svn/fetcher/"
    ],
)