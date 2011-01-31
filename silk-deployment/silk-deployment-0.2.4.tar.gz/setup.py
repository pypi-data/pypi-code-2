#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='silk-deployment',
    version='0.2.4',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
	packages=find_packages(),
    package_dir={'silk': 'silk'},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'silk = silk.utils:cmd_dispatcher',
            'freeze2yaml = silk.utils:freeze_2_yaml',
            'yaml2freeze = silk.utils:yaml_2_freeze',
        ],
    },
	install_requires = [
        'gunicorn',
        'CherryPy',
        'Fabric >= 0.9.2',
        'PyYAML',
        'silk-config',
	],
    url='http://bits.btubbs.com/silk-deployment',
    license='LICENSE.txt',
    description='A Fabric-based tool for deploying WSGI apps on an Ubuntu/Nginx/Supervisord/Gunicorn stack.',
    long_description=open('README.rst').read(),
)

