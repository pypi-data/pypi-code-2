#/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-LocationBase",
    version = "0.2.0",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Simple abstract model for handling longitude/latitude."),
    license = "GPL",
    keywords = "longitude latitude altitude django",
    url = "https://bitbucket.org/weholt/django-locationbase",
    install_requires = ['django', ],
    zip_safe = False,
    classifiers = ["Development Status :: 2 - Pre-Alpha",
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
    packages = ['locationbase'],
    long_description=read('README.txt'),
)