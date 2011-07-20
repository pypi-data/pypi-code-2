#!/usr/bin/env python
# encoding: utf-8

import sys, os

try:
    from distribute_setup import use_setuptools
    use_setuptools()

except ImportError:
    pass

from setuptools import setup, find_packages


if sys.version_info <= (2, 6):
    raise SystemExit("Python 2.6 or later is required.")

if sys.version_info >= (3,0):
    def execfile(filename, globals_=None, locals_=None):
        if globals_ is None:
            globals_ = globals()
        
        if locals_ is None:
            locals_ = globals_
        
        exec(compile(open(filename).read(), filename, 'exec'), globals_, locals_)

else:
    from __builtin__ import execfile

execfile(os.path.join("marrow", "util", "release.py"), globals(), locals())



setup(
        name = "marrow.util",
        version = version,
        
        description = "Commonly shared Python utility subclasses and functions.",
        long_description = """The marrow.util package is a collection of many
useful utility functions, classes, and Python 2 + 3 forwards-compatibility
code.

For full documentation, see the README.textile file present in the package, or
view it online on the GitHub project page:

https://github.com/marrow/marrow.util
""",
        author = "Alice Bevan-McGregor",
        author_email = "alice+marrow@gothcandy.com",
        url = "http://github.com/pulp/marrow.util",
        download_url = "http://pypi.python.org/pypi/marrow.util/",
        license = "MIT",
        keywords = '',
        
        install_requires = [],
        
        test_suite = 'nose.collector',
        tests_require = ['nose', 'coverage'],
        
        classifiers = [
                "Development Status :: 5 - Production/Stable",
                "Environment :: Console",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Programming Language :: Python",
                "Programming Language :: Python :: 2.6",
                "Programming Language :: Python :: 2.7",
                "Programming Language :: Python :: 3",
                "Programming Language :: Python :: 3.1",
                "Programming Language :: Python :: 3.2",
                "Topic :: Software Development :: Libraries :: Python Modules",
                "Topic :: Utilities"
            ],
        
        packages = find_packages(exclude=['tests', 'tests.*', 'docs']),
        include_package_data = True,
        package_data = {
                '': ['Makefile', 'README.textile', 'LICENSE', 'distribute_setup.py'],
                'docs': ['source/*']
            },
        zip_safe = True,
        
        namespace_packages = ['marrow', 'marrow.util'],
    )
