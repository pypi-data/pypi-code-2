#!/usr/bin/env python
from setuptools import setup, find_packages
import os

def read(*path):
    """
    Read and return content from ``path``
    """
    f = open(
        os.path.join(
            os.path.dirname(__file__),
            *path
        ),
        'r'
    )
    try:
        return f.read().decode('UTF-8')
    finally:
        f.close()

setup(
    name='pestotools.genshi',
    description="Genshi integration tools for Pesto",
    long_description=read('README.txt') + '\n\n' + read('CHANGELOG.txt'),
    version=read('VERSION.txt').strip(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
    ],
    keywords='',
    author='Oliver Cope',
    author_email='oliver@redgecko.org',
    url='http://ollycope.com/software/pestotools.genshi/',
    license='BSD',
    namespace_packages=['pestotools'],
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    package_data = {},
    zip_safe=False,
    install_requires=[
        'setuptools',
        'pesto>=18',
        'Genshi',
    ],
    entry_points="""
    [paste.app_factory]
    genshi_app=pestotools.genshi:genshi_app_factory
    """,
)
