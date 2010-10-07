
#!/usr/bin/env python

from setuptools import setup

setup(
    name='pywhere',
    version='0.1',
    description='Find where the hell your Python stuff is',
    author='Ali Afshar',
    author_email='aafshar@gmail.com',
    url='http://bitbucket.org/aafshar/pywhere-main/overview/',
    packages=[],
    scripts=['bin/pywhere'],
    install_requires=['argparse'],
)

