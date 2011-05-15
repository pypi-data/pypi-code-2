#!/usr/bin/env python

from setuptools import setup, find_packages, Extension

setup(name='transcoptract',
    version='1.0',
    description='Transmission Copy Extract Script',
    packages=['transcoptract'],
    entry_points = {
        'console_scripts': [
            'transcoptract = transcoptract.transcoptract:main'
        ]
    },
    install_requires=['transmissionrpc', 'argparse']      
)
