#!/usr/bin/env python

from setuptools import setup

setup(
    name='pongo',
    version='0.1.2',
    description='A Mongo database explorer',
    author='Alberto Granzotto (vrde)',
    author_email='vrde@tastybra.in',
    url='http://bitbucket.org/vrde/pongo',

    packages=[
        'pongo',
    ],
    package_data={'pongo': ['conf/*',
        'views/*',
        'static/css/*',
        'static/img/*',
        'static/js/*']},

    install_requires=[
        'bottle>=0.8.0',
        'pymongo>=1.8',
        'mako>=0.3.0'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
