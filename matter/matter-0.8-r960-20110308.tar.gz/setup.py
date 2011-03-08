#!/usr/bin/env python


"""Structure - objects for storage and manipulation of material structures.

"""

from setuptools import setup, find_packages
import fix_setuptools_chmod

# define distribution
setup(
        name = "matter",
        version = "0.8",
        #namespace_packages = ['matter'],
        packages = find_packages(exclude=['tests']),
        test_suite = 'tests',
        install_requires = [
            'PyCifRW',
        ],
        dependency_links = [
            'http://dev.danse.us/packages/',
        ],

        author = 'J. Brandon Keith',
        author_email = 'jbrkeith@gmail.edu',
        description = "matter classes and parsers for structure formats",
        license = 'BSD',
        keywords = "matter material crystal structure symmetry",
        url = "http://dev.danse.us/trac/inelastic/wiki/crystal",
        download_url = 'http://dev.danse.us/packages/',
        classifiers = [
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'Operating System :: MacOS',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 2.6',
            'Topic :: Scientific/Engineering :: Physics',
        ],
)

# End of file
