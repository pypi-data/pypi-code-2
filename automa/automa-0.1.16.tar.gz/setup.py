# -*- coding: utf-8 -*-

"""Installation script for automa
Run it with
 'python setup.py install', or
 'python setup.py --help' for more options
"""

from setuptools import setup, find_packages
import os, sys

from automa.setup_info import version

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = read('README.txt')

setup(
    name='automa',
    version=version,
    description="Scripting automation utility",
    long_description="""\
Utilty to automate repetitive and/or complex tasks.

It is meant to be simpler than SCons, waf, make, focusing more on robustness,
correctness, and ease of operation than on dependency tracking.
""",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.4',
        'Environment :: Console',
        ],
    keywords='automation build scripting shell',
    author='Marco Pantaleoni',
    author_email='m.pantaleoni@softwarefabrica.org',
    url='http://pypi.python.org/pypi/automa/',
    license='GNU GPL v2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    exclude_package_data = {
        '': ['.bzr'],
    },
    zip_safe=True,
    setup_requires=['setuptools',
                    ],
    install_requires=['setuptools',
                      'argparse',
                      'CmdUtils',
                      'virtualenv>=1.5.1',
                      ],
    extras_require = {
        'ssh':        ['paramiko>=1.7.4',],
        'templates':  ['Jinja2==2.5.5',],
    },
    entry_points = {
        'console_scripts': [
            'automa = automa.main:main',
            ],
        },
)
