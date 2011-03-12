#!/usr/bin/env python
from distutils.core import setup

for cmd in ('egg_info', 'develop', 'upload_sphinx', 'build_sphinx'):
    import sys
    if cmd in sys.argv:
        from setuptools import setup

version='0.6'

setup(
    name='django-fab-deploy',
    version=version,
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['fab_deploy', 'fab_deploy.vcs'],
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
    description = """ Django deployment tool """,

    long_description = open('README.rst').read(),
    requires = ['Fabric (>=1.0.0)', 'jinja2'],

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
