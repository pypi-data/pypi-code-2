from setuptools import setup, find_packages
import os

version = '0.1'

setup(
    name                    = 'bp.rename',
    version                 = version,
    description             = "Command line script to make common file renaming operations easier",
    long_description        = open("README").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
    classifiers             = [
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
    ],
    keywords                = 'command line filesystem',
    author                  = 'Andreas Kaiser',
    author_email            = 'disko@binary-punks.com',
    url                     = 'http://github.com/disko/bp.rename',
    license                 = 'New BSD',
    packages                = find_packages(exclude=['ez_setup']),
    namespace_packages      = ['bp'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = [
        'setuptools',
        # -*- Extra requirements: -*-
        'baker',
        'texttable',
    ],
    entry_points            = """
    # -*- Entry points: -*-
    [console_scripts]
    bp_rename = bp.rename:main
    """,
)
    