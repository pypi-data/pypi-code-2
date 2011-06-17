from distutils.core import setup

setup(
	name = 'bluetrain',
	packages = ['bluetrain'],
	package_data={
		'package': [
		'fixtures/*',
		'templates/*.html',
		'templatetags/*.py',
		],
	},
	version = '0.9.4.6',
	description = 'Django CMS',
	author='Tom Clancy',
	author_email='tclancy@gmail.com',
	url='https://bitbucket.org/tclancy/tkc_apps',
	license = "LGPL",
	classifiers = [
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Framework :: Django"
	],	
)