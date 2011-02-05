from setuptools import setup, find_packages
import os

version  = '0.2'
requires = [
    'setuptools',
    # -*- Extra requirements: -*-
]

setup(
    name                    = 'bp.logging',
    version                 = version,
    description             = "Reduce logging related repetition in your code",
    long_description        = open("README.txt").read() + "\n\n" + open(os.path.join("docs", "HISTORY.txt")).read() + "\n\n" + open(os.path.join("docs", "LICENSE.txt")).read(),
    classifiers             = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ],
    keywords                = 'logging',
    author                  = 'Andreas Kaiser',
    author_email            = 'disko@binary-punks.com',
    url                     = 'https://github.com/disko/bp.logging',
    license                 = 'BSD',
    packages                = find_packages(exclude=['ez_setup']),
    namespace_packages      = ['bp'],
    include_package_data    = True,
    zip_safe                = False,
    install_requires        = requires,
    entry_points            = """
    # -*- Entry points: -*-
    """,
)
