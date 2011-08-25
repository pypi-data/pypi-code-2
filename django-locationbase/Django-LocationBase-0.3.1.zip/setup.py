#/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-LocationBase",
    version = "0.3.1",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Reusable app for handling locations including longitude/latitude, location picking in admin and template tags for static map images."),
    license = "BSD",
    keywords = "longitude latitude altitude django location picking google maps integration",
    url = "https://bitbucket.org/weholt/django-locationbase",
    install_requires = ['django', ],
    zip_safe = False,
    classifiers = ["Development Status :: 2 - Pre-Alpha",
                   'Environment :: Web Environment',
                   'Framework :: Django',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: BSD License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Utilities'],
    packages = ['locationbase'],
    package_data = {
        'locationbase': [
            'static/css/*.css',
            'static/js/*.js',
            'templates/locationbase/location/*.html',
            'templates/admin/locationbase/*.html',
            ],
        },
    long_description=read('README.txt'),
)