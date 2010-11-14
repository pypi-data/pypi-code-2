#!/usr/bin/python
from setuptools import setup

setup(name='ego-boost',
    version='0.1',
    description="Package to track your module's download statistics",
    long_description=open('README').read(),
    author='Sebastian Rahlf',
    author_email='basti at redtoad dot de',
    license='MIT', 
    url='http://pypi.python.org/pypi/ego-boost',
    packages=['egoboost'],
    scripts=['ego-boost'],
    install_requires=[
        'simplejson',
        'lxml'
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Archiving :: Packaging',
        'Topic :: System :: Logging', 
    ]
)
