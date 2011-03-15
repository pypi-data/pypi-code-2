#!/usr/bin/env python
#coding=utf8

from setuptools import setup
import os

ldesc = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
	name='divide',
	version='3',
	description=(''),
	long_description=ldesc,
	keywords='monitoring screen display gtk browser',
	author='Antoine Millet',
	author_email='antoine@inaps.org',
	license='WTFGL',
	scripts=('divide',),
	classifiers=[
		'Development Status :: 5 - Production/Stable',
	]
)
