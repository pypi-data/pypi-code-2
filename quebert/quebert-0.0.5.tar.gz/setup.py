#!/usr/bin/env python

# Copyright (c) 2008-2009 Adroll.com, Valentino Volonghi.
# See LICENSE for details.

"""
Distutils/Setuptools installer for quebert.
"""

try:
    # Load setuptools, to build a specific source package
    from setuptools import setup
except ImportError:
    from distutils.core import setup

install_requires = ["Twisted>=8.0.1"]

description = """\
"""

setup(
    name = "quebert",
    author = "Valentino Volonghi",
    author_email = "valentino@adroll.com",
    url = "http://adroll.com/labs",
    description = description,
    license = "MIT License",
    version="0.0.5",
    install_requires=install_requires,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Internet',
    ],
    packages=["quebert", "quebert.test", "twisted"],
    package_data={'twisted': ['plugins/quebert_plugin.py',
                              'plugins/qexec_plugins.py']},
    include_package_data=True,
    zip_safe=False
)
