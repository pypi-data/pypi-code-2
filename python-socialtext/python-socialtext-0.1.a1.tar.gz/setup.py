import os
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = read("requirements.txt")
if sys.version_info < (2,6):
    requirements.append('simplejson')

setup(
    name = "python-socialtext",
    version = "0.1.a1",
    description = "Client library for Socialtext's ReST API",
    long_description = read('README.rst'),
    author = 'Justin Murphy, The Hanover Insurance Group',
    author_email = 'ju1murphy@hanover.com',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = requirements,
    
    tests_require = ["nose", "mock"],
    test_suite = "nose.collector",
)