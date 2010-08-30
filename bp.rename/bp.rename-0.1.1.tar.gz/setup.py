from setuptools import setup, find_packages
import sys, os

here    = os.path.abspath(os.path.dirname(__file__))
README  = open(os.path.join(here, 'README.txt')).read()
NEWS    = open(os.path.join(here, 'NEWS.txt')).read()

version = '0.1.1'

install_requires = [
    # List your project dependencies here.
    # For more details, see:
    # http://packages.python.org/distribute/setuptools.html#declaring-dependencies
    'baker >= 1.1',
    'texttable >= 0.7.0',
]

setup(
    name                    = 'bp.rename',
    version                 = version,
    description             = "Command line script to make common file renaming operations easier",
    long_description        = README + '\n\n' + NEWS,
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
    license                 = 'BSD',
    packages                = find_packages('src'),
    package_dir             =  {'': 'src'},
    namespace_packages      =  ['bp'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = install_requires,
    entry_points            = {
        'console_scripts':
            ['bp_rename=bp.rename:main']
    }
)
