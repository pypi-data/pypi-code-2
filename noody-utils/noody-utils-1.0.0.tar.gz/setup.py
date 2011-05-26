#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

from noody.app import VERSION

setup(
    name = 'noody-utils',
    version = VERSION,
    description = u"Utility commands for manage Noody sessions from" \
                  u" unix-like shell.",
    license = 'BSD',
    author = 'Simone Dalla',
    author_email = 'sdalla@comune.zolapredosa.bo.it',
    url = 'https://bitbucket.org/ced_zola/noody-utils',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Plugins',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Natural Language :: Italian',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: System :: Networking',
        'Topic :: System :: Shells',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    namespace_packages = ['noody'],
    entry_points = {
        'console_scripts' : [
            'open-noody-session = noody.app:open'
        ]
    },
    install_requires = [],
    test_suite = ''
)