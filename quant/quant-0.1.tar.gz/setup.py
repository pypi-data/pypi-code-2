#!/usr/bin/env python
import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, './src')
from quant import __version__

basePath = os.path.abspath(os.path.dirname(sys.argv[0]))
scripts = [ 
    os.path.join('bin', 'quant-makeconfig'),
    os.path.join('bin', 'quant-admin'),
    os.path.join('bin', 'quant-test'),
]

setup(
    name='quant',
    version=__version__,

    package_dir={'': 'src'},
    packages=find_packages('src'),
    scripts=scripts,
    # just use auto-include and specify special items in MANIFEST.in
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        'domainmodel==0.9',
        'python-dateutil',
        # Installing scipy with setuptools doesn't work.
        #'scipy', 
        #'numpy',
    ],
    author='Appropriate Software Foundation',
    author_email='john.bywater@appropriatesoftware.net',
    license='GPL',
    url='http://appropriatesoftware.net/quant',
    description='Enterprise architecture for quantitative analysis',
    long_description =\
"""
""",
    classifiers = [
#        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
#        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
#        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
