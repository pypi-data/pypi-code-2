from setuptools import setup, find_packages
import sys, os

version = '0.0'
from ckanext.dataapi import __version__, __doc__ as long_description

setup(
	name='ckanext-dataapi',
	version=__version__,
	description=long_description.split('\n')[0],
	long_description=long_description,
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='CKAN Team (Open Knowledge Foundation)',
	author_email='ckan@okfn.org',
	url='http://ckan.org/',
	license='mit',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.dataapi'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	dataapi=ckanext.dataapi:DataAPIPlugin
	datapreview=ckanext.dataapi:DataPreviewPlugin
	""",
)
