#!/usr/bin/env python
# -*- coding: utf-8 -


import os
from setuptools import setup


setup(
    name='django-cherrydev',
    version='0.1b',

    description='CherryPy Web server for Django development.',
    long_description = file(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author='David Bennett',
    author_email='david@db-init.com',
    license='MIT',
    url='http://code.db-init.com/django-cherrydev/',

    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development :: '
                 'Libraries :: Python Modules',
                 'Topic :: Utilities'],
    packages=['cherrydev'],

    entry_points="""
    [console_scripts]
    cherrydev=cherrydev:main
    """,
    )
