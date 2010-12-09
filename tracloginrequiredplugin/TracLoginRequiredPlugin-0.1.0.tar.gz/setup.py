#!/usr/bin/env python

from setuptools import setup

setup(
	name='TracLoginRequiredPlugin',
	version='0.1.0',
	author='David A. Riggs',
	author_email='david.riggs@createtank.com',
	url='https://code.google.com/p/tracloginrequiredplugin/',
	download_url='https://code.google.com/p/tracloginrequiredplugin/',
	description='Trac plugin which redirects all unauthenticated requests to the login page',
	long_description=open('README.txt').read(),
	install_requires = ['Trac >= 0.11'],
	packages=['loginrequired'],
	entry_points = '''
		[trac.plugins]
		loginrequired = loginrequired
	''',
	classifiers=[
				'Development Status :: 3 - Alpha',
				'Environment :: Plugins',
				'Framework :: Trac',
				'Intended Audience :: System Administrators',
				'License :: OSI Approved :: GNU General Public License (GPL)',
				'Natural Language :: English',
				'Operating System :: OS Independent',
				'Programming Language :: Python',
				'Programming Language :: Python :: 2',
				'Programming Language :: Python :: 2.5',
				'Topic :: System :: Systems Administration :: Authentication/Directory'
				],
)
