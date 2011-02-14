import os
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-socialtext",
    version = "0.1",
    description = "Django application to integrate Socialtext into your project.",
    long_description = read('README.rst'),
    author = 'Justin Murphy, The Hanover Insurance Group',
    author_email = 'ju1murphy@hanover.com',
    packages = find_packages(),
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Django',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = read("requirements.txt"),
)