#!/usr/bin/python

from setuptools import setup, find_packages

import os

try:
	desc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read().strip()
except:
	desc = 'Affect multiple Mercurial repos simultaneously'

setup(
	name='multirepo',
	version='1.0rc2',
	py_modules=['multirepo'],
	author='Iain Lowe',
	author_email='iain.lowe@gmail.com',
	description='Mercurial extension to affect multiple repositories simultaneously.',
	long_description=desc,
	zip_safe=True,
	url='http://bitbucket.org/ilowe/multirepo',
	download_url='http://bitbucket.org/ilowe/multirepo/downloads',
	license='MIT',
	keywords='hg scm mercurial multirepo multiple',
)
