
#!/usr/bin/env python

from setuptools import setup

setup(
    name='Fom',
    version='0.8',
    description='FluidDB API and Object Mapper',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    url='http://bitbucket.org/aafshar/fom-main/overview/',
    packages=['fom'],
    scripts=['bin/fdbc'],
    install_requires=['httplib2', 'blinker'],
)

