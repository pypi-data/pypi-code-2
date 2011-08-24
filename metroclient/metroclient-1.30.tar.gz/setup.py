#!/usr/bin/env python

from distutils.core import setup

setup(name='metroclient',
    version = '1.30',
    author = 'AppHosted Team',
    author_email = 'support@apphosted.com',
    packages = ['metroclient'],
    description = 'AppHosted application deployment utility',
    url = 'https://apphosted.com',
    license = 'License :: OSI Approved :: GNU General Public License (GPL)',
    long_description = """
    Metro is the application deployment utility for managing and deploying web applications
    hosted on http://apphosted.com""",
    download_url = 'https://metro.apphosted.com/client/get/',
    scripts = ['metro'],
    package_data = {
        'metroclient': ['*.txt'],
    },
    install_requires = ['httplib2','paramiko'],
    platforms = [
        "All",
        ],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Utilities",
        ]
    )

