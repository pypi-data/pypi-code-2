from setuptools import setup, find_packages
import sys, os

version = '0.1'
from ckanext.datapreview import __version__, __doc__ as long_description

setup(
	name='ckanext-datapreview',
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
	namespace_packages=['ckanext', 'ckanext.datapreview'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
    [ckan.plugins]
	# Add plugins here, eg
	datapreview=ckanext.datapreview:DataPreviewPlugin
	""",
)
