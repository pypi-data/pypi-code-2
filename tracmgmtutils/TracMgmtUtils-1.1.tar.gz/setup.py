from setuptools import find_packages, setup

setup(
	name = 'TracMgmtUtils', version='1.1',
	description = "Utility functions for managing Trac instances",
	author = "Stefan Richter",
	author_email = "stefan@02strich.de",
	url = "http://www.02strich.de",
	license = "PSF",
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Framework :: Trac',
		'Intended Audience :: Developers',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: Python Software Foundation License',
		'Programming Language :: Python :: 2',],
	
	packages = find_packages(exclude=['*.tests*']),
	#install_requires=['Paper>=1.0'],
)

