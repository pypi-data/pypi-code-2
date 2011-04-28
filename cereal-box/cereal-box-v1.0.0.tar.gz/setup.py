from setuptools import setup

setup(
	name = 'cereal-box',
	packages = ['cereal',],
	version = 'v1.0.0',
	author = 'RED Interactive Agency',
	author_email = 'geeks@ff0000.com',

	url = 'http://www.github.com/ff0000/cereal-box/',
	download_url = 'http://www.github.com/ff0000/cereal-box/',

	license = 'MIT license',
	description = 'Data feed library for Django models.',

	long_description = open('README.markdown').read(),
	requires = [],

	classifiers = (
		'Development Status :: 3 - Alpha',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	),
)
