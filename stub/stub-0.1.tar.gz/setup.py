#!/usr/bin/python

from setuptools import setup, find_packages

setup(
	name='stub',
	version='0.1',
	packages=find_packages(),
	author='Iain Lowe',
	author_email='iain.lowe@gmail.com',
	description='Temporarily modify callable behaviour and object attributes.',
	license='MIT',
	url='https://bitbucket.org/ilowe/stub',
	test_suite='stubtests',
	keywords='test testing stub mock virtual simulate decorate',
)
