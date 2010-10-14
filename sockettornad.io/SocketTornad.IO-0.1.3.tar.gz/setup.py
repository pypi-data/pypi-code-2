#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

try:
    license = open('LICENSE').read()
except:
    license = None

try:
    readme = open('README.rst').read()
except:
    readme = None

setup(
    name='SocketTornad.IO',
    version='0.1.3',
    author='Brendan W. McAdams',
    author_email='bwmcadams@evilmonkeylabs.com',
    packages=['tornad_io', 'tornad_io.websocket'],
    scripts=[],
    url='http://github.com/SocketTornadIO/SocketTornad.IO',
    license=license,
    description='Python implementation of the Socket.IO protocol for the Tornado webserver/framework.',
    long_description=readme,
    requires=['pyCLI', 'simplejson', 'tornado', 'beaker'],
    install_requires=[
        'pyCLI >= 1.1.1',
        'simplejson >= 2.1.0', # Decimal support
        'tornado >= 1.1.0',
        'beaker >= 1.5.3'
    ]
)
