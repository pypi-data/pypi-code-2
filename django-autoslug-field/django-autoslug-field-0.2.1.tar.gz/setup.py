#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'django-autoslug-field',
    version = '0.2.1',
    description = "AutoSlugField for Django based on django-extensions AutoSlugField, adds option to track foreignkey/parent field for slug.",
    long_description = open('README.rst').read(),
    author = 'Aljosa Mohorovic',
    author_email = 'aljosa.mohorovic@gmail.com',
    url='http://github.com/aljosa/django-autoslug-field/',
    packages = find_packages(),
    include_package_data = True,
    license = "MIT License",
    keywords = "django autoslug slug field",
    platforms = ['any'],
)
