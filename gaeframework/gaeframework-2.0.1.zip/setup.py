#!/usr/bin/env python
#from distutils.core import setup
from setuptools import setup, find_packages
#from distutils.command.install_data import install_data
import os
import sys


def fullsplit(path, result=None):
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []

for dir_name in [f for f in os.listdir(os.path.dirname(__file__) or '.') if os.path.isdir(f)]:
    for dirpath, dirnames, filenames in os.walk(dir_name):
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

with open('README') as file:
    long_description = file.read()


setup(
    name = "gaeframework",
    version = "2.0.1",
    author = "Anton Danilchenko",
    author_email = "anton.danilchenko@gaeframework.com",
    description = "GAE framework is a Python web application framework for use on Google App Engine",
    long_description = long_description,
    download_url = "http://gaeframework.googlecode.com/files/gaeframework-2.0.1.zip",
    url = "http://wwww.gaeframework.com",
#    packages = packages,
    packages = find_packages(),
#    data_files = data_files,
    include_package_data = True,
    zip_safe=False,
#    package_data = {
#        '': ['*.txt', '*.yaml', '*.*', 'VERSION'],
#    },
    scripts = ['gae-manage.py'],
    classifiers=['Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Programming Language :: Python :: 2.6',
                'Programming Language :: Python :: 2.7',
                'Topic :: Internet :: WWW/HTTP',
                'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
                'Topic :: Internet :: WWW/HTTP :: WSGI',
                'Topic :: Software Development :: Libraries :: Application Frameworks',
                'Topic :: Software Development :: Libraries :: Python Modules',
                ]
)
