#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name = 'django-hierarchical',
	version = '0.1.1',
	description = 'Hierarchical models and form fields for Django',
	author = 'Moxy Park',
	author_email = 'moxypark@me.com',
	url = 'http://moxypark.co.uk/',
	packages = find_packages(),
	package_dir = {
		'django_hierarchy': 'django_hierarchy'
	},
	install_requires = [
		'django>=1.2.1'
	]
)