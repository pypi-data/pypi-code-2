from setuptools import setup, find_packages
import os

version = '0.1'

setup(
    name                    = 'bp.tagging',
    version                 = version,
    description             = "Multimedia file tagging library",
    long_description        = open("README.txt").read() + "\n" + open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers             = [
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Utilities",
    ],
    keywords                = 'mp3 mp4 id3',
    author                  = 'binary punks',
    author_email            = 'disko@binary-punks.com',
    url                     = 'http://github.com/disko/bp.tagging',
    license                 = 'BSD',
    packages                = find_packages(exclude=['ez_setup']),
    namespace_packages      = ['bp'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = [
        'setuptools',
        # -*- Extra requirements: -*-
        'baker',
        'mutagen',
        'odict',
        'texttable',
    ],
    entry_points            = """
    # -*- Entry points: -*-
    [console_scripts]
    bp_tagging = bp.tagging:main
    """,
)
    