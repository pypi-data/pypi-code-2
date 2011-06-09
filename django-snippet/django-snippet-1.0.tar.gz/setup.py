#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name = 'django-snippet',
	version = '1.0',
	#packages = ['snippet',],
	packages = find_packages(),
	include_package_data = True,
	author = 'Shu Zong Chen',
	author_email = 'shu.chen@freelancedreams.com',
	description = 'Drop-in snippets for django project',
	long_description = \
"""
Drop-in Snippets for Django

Snippets are little placeholders for lines or blocks
of content to be managed using the django admin.

Place {% snippet "name" %} templatetags in your
templates and they get automatically added in the
admin.

Features:

* Optional default value
* Snippetblock templatetag to enclose longer defaults
""",
	license = "MIT License",
	keywords = "django templatetag snippets snippet",
	classifiers = [
		'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Software Development :: Libraries :: Python Modules',
	],
	platforms = ['any'],
	url = 'https://bitbucket.org/sirpengi/django-snippets',
	download_url = 'https://bitbucket.org/sirpengi/django-snippets/downloads',
)

