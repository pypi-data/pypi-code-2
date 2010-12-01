#!/usr/bin/env python
from setuptools import setup, find_packages
import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name = "django-output-validator",
    version = '1.5',
    packages = find_packages(),
    include_package_data = True,

    author = "Luke Plant",
    author_email = "L.Plant.98@cantab.net",
    url = "http://lukeplant.me.uk/resources/djangovalidator/",
    description = "App to catch HTML errors (or other errors) in outgoing Django pages.",
    long_description = (
                        read('README.rst')
                        + "\n\n" +
                        read('CHANGES.rst')
    ),
    license = "MIT",
    keywords = "django HTML XHTML validation validator",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries",
        "Topic :: Software Development :: Testing",
        ]
)
