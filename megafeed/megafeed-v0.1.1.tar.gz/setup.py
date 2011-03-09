from setuptools import setup, find_packages

setup(
	name = 'megafeed',
	packages = find_packages(exclude=['ez_setup', 'examples', 'tests']),
	version = 'v0.1.1',
	author = 'RED Interactive Agency',
	author_email = 'geeks@ff0000.com',
	
	url = 'http://www.github.com/ff0000/megafeed/',
	download_url = 'http://www.github.com/ff0000/megafeed/',

	license = 'MIT license',
	description = 'A library for serializing complex django querysets.',

	long_description = open('README.md').read(),
	requires = [],

	classifiers = (
		'Development Status :: 4 - Beta',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Programming Language :: Python',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	),
)

