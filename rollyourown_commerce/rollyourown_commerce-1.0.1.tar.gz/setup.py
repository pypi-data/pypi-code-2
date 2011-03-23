#!/usr/bin/env python
# -*- coding: UTF-8 -*-

try:
    import ez_setup
    ez_setup.use_setuptools()
except ImportError:
    pass

from setuptools import setup, find_packages
setup(
    name = "rollyourown_commerce",
    version = "1.0.1",
    packages = find_packages(exclude=["docs*", "tests*", "examples*"]),
    namespace_packages = ["rollyourown"],
    install_requires = ['django>=1.0'],
    author = "Will Hardy",
    author_email = "rollyourown@willhardy.com.au",
    description = "A framework to ease development of hand rolled ecommerce applications with Django.",
    long_description = open('README.txt').read(),
    license = "LICENSE.txt",
    keywords = "ecommerce, django, framework",
    url = "https://github.com/willhardy/Roll-Your-Own",
    include_package_data = True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],

)

