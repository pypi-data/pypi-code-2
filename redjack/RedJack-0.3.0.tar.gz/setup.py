#!/usr/bin/python

from setuptools import setup
import glob

setup(
    name='RedJack',
    version='0.3.0',
    author='Michal Nowikowski',
    author_email='godfryd@gmail.com',
    packages=['redjack'],
    include_package_data=True,
    url='http://redjacklab.net/',
    license='LICENSE.txt',
    description='RedJack - continuous integration system.',
    long_description=open('README.txt').read(),
    install_requires=['pyyaml>3.0', 'mako'],
    entry_points = {
        'console_scripts': [
            'rjserver = redjack.server:main',
            'rjagent = redjack.agent:main',
        ]
    }

)
