#!/usr/bin/env python
from distutils.core import setup

for cmd in ('egg_info', 'develop'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

version = '0.1'

setup(
    name='django-vkontakte-merchant',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['merchant_api', 'merchant_api.migrations'],

    url='http://bitbucket.org/kmike/django-vkontakte-merchant/',
    download_url = 'http://bitbucket.org/kmike/django-vkontakte-merchant/get/tip.gz',
    license = 'MIT license',
    description = 'Vkontakte Merchant API django app',
    long_description = open('README.rst').read().decode('utf8'),

    requires = ["vkontakte(>=0.9.5)"],

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: Russian',
    ),
)
