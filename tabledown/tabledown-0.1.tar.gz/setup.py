# -*- coding: utf-8 -*-


requires = ['xlrd>=0.7.1', 'xlwt>=0.7.2']

import sys
python_version = sys.version_info[:2]

from setuptools import setup, find_packages

the_url = 'http://code.google.com/p/tabledown/'

def mkargs(**kwargs):
    return kwargs

args = mkargs(
    name = 'tabledown',
    version = '0.1',
    author = 'T.C. Chou',
    author_email = 'tcchou@tcchou.org',
    url = the_url,
    packages = ['tabledown'],
    description = 'Extract data from spreadsheets to collections(lists, and hashes), and vice versa.',
    long_description = \
        "Library for developers to extract data from spreadsheet files " \
        "to general data structures(i.e. lists, hashes), and vice versa.",
    platforms = ["Any platform -- don't need Windows"],
    license = 'BSD',
    keywords = ['xls', 'spreadsheet', 'collections'],
    install_requires = requires,
    )

if python_version >= (2, 3):
    args23 = mkargs(
        download_url = the_url,
        classifiers = [
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Operating System :: OS Independent',
            'Topic :: Database',
            'Topic :: Office/Business',
            'Topic :: Software Development :: Libraries :: Python Modules',
            ],
        )
    args.update(args23)

if python_version >= (2, 4):
    args24 = mkargs(
        packages=find_packages(),
        include_package_data=True,
        #package_data={
        #    'tabledown': [
        #        'doc/*.htm*',
        #        ],
        #    },
        )
    args.update(args24)

setup(**args)
