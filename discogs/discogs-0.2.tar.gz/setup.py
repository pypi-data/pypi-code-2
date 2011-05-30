#!/usr/bin/env python

from setuptools import setup

setup(
        name='discogs',
        version='0.2',
        description='Python interface to the Discogs music information database.',
        author='Jeremy Cantrell',
        author_email='jmcantrell@gmail.com',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Communications :: Email :: Email Clients (MUA)',
            'Topic :: System :: Systems Administration',
            'Topic :: Utilities',
            ],
        entry_points={
            'console_scripts': [
                'discogs=discogs:main',
                ]
            },
        py_modules=[
            'discogs',
            ],
        )
