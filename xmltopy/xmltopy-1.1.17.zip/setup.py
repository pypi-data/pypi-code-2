from setuptools import setup
import os
import xmltopy

setup(
    name='xmltopy',
    version = xmltopy.__version__,
    description = 'Utilities for manipulating XML',
    author = 'Matt Hanger',
    author_email = 'matt@matthanger.net',
    license = 'MIT',
    url ='http://code.google.com/p/xmltopy/',
    packages = ['xmltopy'],
    scripts = ['xsdtopy.py',],
    include_package_data = True,
    zip_safe = False,
    install_requires = ['lxml>=2.2', 'jinja2', 'iso8601',],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',],
)