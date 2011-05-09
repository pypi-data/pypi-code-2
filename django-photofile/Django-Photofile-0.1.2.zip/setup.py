#/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-Photofile",
    version = "0.1.2",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Templatetags for thumbnail generation, with automatic rotation based on EXIF.Orientation."),
    license = "GPL",
    keywords = "photo thumbnail generation django metadata",
    url = "https://bitbucket.org/weholt/django-photofile",
    install_requires = ['django', 'pil',],
    zip_safe = False,
    classifiers = ["Development Status :: 2 - Pre-Alpha",
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
    packages = find_packages(),
    long_description=read('README.txt'),
)