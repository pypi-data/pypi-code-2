#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# setup.py - Setup file for the kurzfile package
#


import os
import sys

scripts = ['kurzfile/scripts/k2list.py']

if sys.platform.startswith('win') and 'py2exe' in sys.argv:
    try:
        from distutils.core import setup
        import py2exe
    except ImportError:
        print >>sys.stderr, ("py2exe not found. Cannot build Windows "
            "stand-alone executables without it. Please install py2exe.")
        sys.exit(1)
    else:
        setup_opts = dict(
            options = {'py2exe': {'bundle_files': 1}},
            console = scripts,
            zipfile = None)
else:
    try:
        import ez_setup
        ez_setup.use_setuptools()
        from setuptools import setup
        setup_opts = dict(
            entry_points = {
                'console_scripts': [
                    'k2list = kurzfile.scripts.k2list:main'
                ]
            },
            zip_safe=True
        )
    except ImportError:
        from distutils.core import setup
        setup_opts = dict(scripts=scripts)

execfile(os.path.join('kurzfile', 'release.py'), {}, setup_opts)

setup(
    packages = ['kurzfile', 'kurzfile.scripts'],
    **setup_opts
)
