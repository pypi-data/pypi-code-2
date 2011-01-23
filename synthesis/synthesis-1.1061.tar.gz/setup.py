#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages
import sys

version = '1.1061'

install_requires = [
    'setuptools',
]

#ECJ20100920 needed to remove this hard-coded dependency condition, since pyinotify 0.8.8 isn't installing, whilst 0.9.0 seems to work fine
#if sys.platform.startswith("linux"):
#    install_requires.append("pyinotify==0.8.8")

setup(
    name = 'synthesis',
    version = version,
    description='Health and Human Services Data Integration Server',
    license = 'MIT',
    platforms = 'Linux',
    author='Alexandria Consulting LLC',
    author_email='eric@alexandriaconsulting.com',
    url='http://xsd.alexandriaconsulting.com/repos/trunk/synthesis/src',
    packages = ['synthesis', 'synthesis.conf', 'synthesis.errcatalog'],
    #namespace_packages=[],
    #packages = find_packages('src'),
    #package_dir = {'': 'src'},
    #include_package_data = True,
    #install_requires = install_requires,
    long_description="""Synthesis is a Health and Human Services Data Integration Server. It moves us closer to the vision of seamless human services data integration. Synthesis currently imports and exports HUD HMIS formats, but could be extended to handle any human services data formats. Eventually will handle the nascent NIEM Human Services format. Composed of a REST web service. Also can listen for received FTP files.""",
    classifiers=[
      "Programming Language :: Python",
    ],
    keywords='human services data integration hmis 211 niem',
    install_requires=[
    'setuptools',
    ]
    )
    
