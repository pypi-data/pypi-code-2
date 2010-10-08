from setuptools import setup, find_packages
import sys, os

here    = os.path.abspath(os.path.dirname(__file__))
README  = open(os.path.join(here, 'doc', 'README.txt')).read()
NEWS    = open(os.path.join(here, 'doc', 'NEWS.txt')).read()

version = '0.1'

install_requires = [
    "cmdln >= 1.1.2",
]


setup(
    name                    = 'bp.convert.movie',
    version                 = version,
    description             = "Command line utility to ease movie conversion with HandBrakeCLI",
    long_description        = README + '\n\n' + NEWS,
    classifiers             = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
    ],
    keywords                = '',
    author                  = 'Andreas Kaiser',
    author_email            = 'disko@binary-punks.com',
    url                     = 'http://github.com/disko/bp.convert.movie',
    license                 = 'BSD',
    packages                = find_packages('src'),
    package_dir             = {'': 'src'},
    namespace_packages      = ['bp', 'bp.convert'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = install_requires,
    entry_points            = {
        'console_scripts':
            ['bp_convert_movie=bp.convert.movie:main']
    }
)
