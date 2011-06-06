#!/usr/bin/env python
from setuptools import setup

setup(
    name = "frontweb",
    version = "0.4",
    author='Hugo Ruscitti',
    author_email='hugoruscitti@gmail.com',
    description='A simple website builder using restructured text',
    url='http://www.frontweb.com.ar',
    install_requires=['yapsy'],

    packages=['frontweb', 'frontweb.directives', 'frontweb.yapsy',
              'frontweb.management.commands'],
    scripts=['bin/frontweb', 'frontweb/management/commands/frontweb_plugin.py'],
    license='GPLv3',

    include_package_data = True,
    package_data = {
                    'data': ['frontweb/data/*', 'frontweb/templates/*',
                             'frontweb/plugins/*', 'frontweb/tests/*',
                               ]
                   },
    )
