#!/usr/bin/env python
from setuptools import setup

setup(
    name = "frontweb",
    version = "0.3",
    author='Hugo Ruscitti',
    author_email='hugoruscitti@gmail.com',
    description='A simple website builder using restructured text',
    url='http://www.frontweb.com.ar',
    install_requires=['django'],

    packages=['frontweb', 'frontweb.directives', 'frontweb.yapsy'],
    scripts=['bin/frontweb'],
    license='GPLv3',

    include_package_data = True,
    package_data = {
                    'data': ['frontweb/data/*', 'frontweb/templates/*', 
                             'frontweb/plugins/*', 'frontweb/tests/*',
                               ]
                   },
    )
