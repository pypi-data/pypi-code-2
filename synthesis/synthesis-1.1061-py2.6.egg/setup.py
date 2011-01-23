#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages
import sys

version = '1.106'

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
    author='Alexandria Consulting LLC',
    author_email='eric@alexandriaconsulting.com',
    url='http://xsd.alexandriaconsulting.com/repos/trunk/synthesis/src',
    packages = ['synthesis', 'synthesis.conf', 'synthesis.errcatalog']
    #namespace_packages=[],
    #packages = find_packages('src'),
    #package_dir = {'': 'src'},
    #include_package_data = True,
    #install_requires = install_requires,
    )
    
long_description="""Health and Human Services Data Integration Server""",
classifiers=[
      "License :: OSI Approved :: The MIT License",
      "Programming Language :: Python",
      "Intended Audience :: Human Services Practitioners",
      "Topic :: Human Services Data Integration",
],
keywords='human services data integration hmis 211 niem',
license='MIT',
install_requires=[
    'setuptools',
    ]

    
