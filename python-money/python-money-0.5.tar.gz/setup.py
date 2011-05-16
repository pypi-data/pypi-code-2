import os
from setuptools import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "python-money",
	version = "0.5",
	author = "Jordan Dimov",
	author_email = "s3x3y1@gmail.com",
	maintainer = "Ben Coughlan",
	maintainer_email = "ben.coughlan@gmail.com",
	description = ("Data classes to represent Money and Currency types"),
	license = "BSD",
	keywords = "money currency",
	url = "http://code.google.com/p/python-money",
	packages = ['money', 'money.django'],
	long_description = read('README.txt'),
	classifiers = [
		"Development Status :: 4 - Beta",
		"Environment :: Plugins",
		"Environment :: Other Environment",
		"Framework :: Django",
		"Operating System :: OS Independent",
		"Intended Audience :: Developers",
		"Intended Audience :: Financial and Insurance Industry",
		"License :: OSI Approved :: BSD License",
		"Programming Language :: Python",
		"Topic :: Office/Business :: Financial",
	]
)
