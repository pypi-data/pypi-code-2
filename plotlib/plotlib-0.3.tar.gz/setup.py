#!/usr/bin/env python


"""Vnf Plotlib - Plotting utitilites for Vnf (Virtual Neutron Facility) scripting.

"""

from setuptools import setup, find_packages

# define distribution
setup(
        name = "plotlib",
        version = "0.3",
        namespace_packages = ['plotlib'],
        packages = find_packages(exclude=['tests']),
        test_suite = 'tests',
#        install_requires = [
#            'PyCifRW',
#        ],
#        dependency_links = [
#            'http://www.diffpy.org/packages/',
#        ],
        author = 'J. Brandon Keith',
        author_email = 'jbrkeith@gmail.edu',
        description = """A plotting toolkit for VSAT data objects""",
        license = 'BSD',
        keywords = "plot scattering",
        url = "http://docs.danse.us/inelastic/vsat/",
        download_url = 'http://dev.danse.us/packages/',
        classifiers = [
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 3 - Alpha',
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
