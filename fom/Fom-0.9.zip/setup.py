
#!/usr/bin/env python

from setuptools import setup
from fom.version import version

setup(
    name='Fom',
    version=version,
    description='FluidDB API and Object Mapper',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    url='http://bitbucket.org/aafshar/fom-main/overview/',
    packages=['fom'],
    scripts=['bin/fdbc'],
    install_requires=['httplib2', 'blinker'],
)

