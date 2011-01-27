#!/usr/bin/env python
from distutils.core import setup

version='0.0.10'

setup(
    name='django-fab-deploy',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['fab_deploy'],

    url='http://bitbucket.org/kmike/django-fab-deploy/',
    download_url = 'http://bitbucket.org/kmike/django-fab-deploy/get/tip.zip',
    license = 'MIT license',
    description = """ Opinionated django deployment tool """,

    long_description = open('README.rst').read(),
    requires = ['Fabric', 'jinja2', 'South'],

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
