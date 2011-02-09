#!/usr/bin/env python
from distutils.core import setup

for cmd in ('egg_info', 'develop', 'upload_sphinx', 'build_sphinx'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

version='0.2'

setup(
    name='django-fab-deploy',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['fab_deploy'],
    package_data={
        'fab_deploy': [
            'config_templates/*.config',
            'config_templates/*.py',
            'config_templates/hgrc',
            'example_reqs/*.txt',
        ]
    },

    scripts = ['bin/django-fab-deploy'],

    url='https://bitbucket.org/kmike/django-fab-deploy/',
    download_url = 'https://bitbucket.org/kmike/django-fab-deploy/get/tip.zip',
    license = 'MIT license',
    description = """ Opinionated django deployment tool """,

    long_description = open('README.rst').read(),
    requires = ['Fabric', 'jinja2'],

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
