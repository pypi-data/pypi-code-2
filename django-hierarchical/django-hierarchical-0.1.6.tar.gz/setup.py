#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name = 'django-hierarchical',
	version = '0.1.6',
	description = 'Hierarchical models and form fields for Django',
	author = 'Moxy Park',
	author_email = 'moxypark@me.com',
	url = 'http://moxypark.co.uk/',
	packages = find_packages(),
	package_dir = {
		'django_hierarchy': 'django_hierarchy'
	},
	classifiers = [
		'Development Status :: 3 - Alpha',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		# 'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Framework :: Django',
    ]
)