#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='django-hstsmiddleware',
    version='1.0',
    description=('Implement HSTS to force the use of HTTPS.'),
    long_description=open('README.rst', 'r').read(),
    author='TrustCentric',
    author_email='admin@trustcentric.com',
    url='http://bitbucket.org/trustcentric/django-hstsmiddleware/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['django_hstsmiddleware'],
    zip_safe=True,
    install_requires=['Django>=1.3']
)
