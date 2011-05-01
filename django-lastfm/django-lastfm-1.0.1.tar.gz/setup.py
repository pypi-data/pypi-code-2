#! /usr/bin/env python
# encoding: utf-8
from distutils.core import setup
import sys
reload(sys).setdefaultencoding('Utf-8')


setup(
    name='django-lastfm',
    version='1.0.1',
    author='Stefan Scherfke',
    author_email='stefan at sofa-rockers.org',
    description='Access Last.fm from your Django site.',
    long_description=open('README.txt').read(),
    url='http://stefan.sofa-rockers.org/django-lastfm/',
    download_url='http://bitbucket.org/scherfke/django-lastfm/downloads/',
    license='BSD',
    packages=[
        'lastfm',
        'lastfm.templatetags',
    ],
    package_data={
        'lastfm': ['templates/lastfm_widget/*'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
