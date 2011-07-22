#!/usr/bin/env python

from distutils.core import setup


description = "Helpful Django utilities from Discovery Creative"

VERSION = '1.3'

setup(
    name='django-disco',
    version=VERSION,
    author='Joshua Ourisman',
    author_email='josh@joshourisman.com',
    url='https://bitbucket.org/discovery/django-disco',
    description=description,
    long_description=description,
    license='BSD',
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
    packages=['disco_utils', ],
    package_data = {'disco_utils': ['templatetags/*',],},
    install_requires=['django', 'django-native-tags',],
    )
