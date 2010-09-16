try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup, find_packages

import sys, os
from rootplot import __version__

setup(
    name         = 'rootplot',
    version      = __version__,
    description  = "Tools for quick and beautiful plotting with ROOT",
    long_description = (
        "Includes command-line scripts and an API for easily producing "
        "complex canvases from ROOT histograms along with tools for producing "
        "histograms from TTrees and quickly displaying the contents of a ROOT "
        "file and a library for producing matplotlib figures from ROOT input."
        ),
    author       = 'Jeff Klukas',
    author_email = 'klukas@wisc.edu',
    url          = 'http://packages.python.org/rootplot/',
    download_url = '',
    packages = find_packages('lib'),
    package_dir = {'': 'lib'},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'rootplot = rootplot.core:cli_rootplot',
            'rootplotmpl = rootplot.core:cli_rootplotmpl',
            'tree2hists = rootplot.tree2hists:main',
            'rootinfo = rootplot.rootinfo:main'
            ]
        },
    classifiers  = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
        ],
    )
