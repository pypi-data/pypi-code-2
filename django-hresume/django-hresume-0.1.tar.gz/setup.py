import os
from setuptools import setup, find_packages

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name = "django-hresume",
	version = "0.1",
	url = "http://github.com/wscoble/django-hresume",
	license = "LGPL",
	description = "A resume application for django, presented using the hresume microformat",
	long_description = read("README"),
	author = "Scott Scoble",
	author_email = "sscoble@scottfolio.us",
	packages = find_packages("src"),
	package_dir = {"": "src"},
	install_requires = ["setuptools"],
	classifiers = [
		"Development Status :: 1 - Planning",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
		"Natural Language :: English",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Internet :: WWW/HTTP",
	]
)
