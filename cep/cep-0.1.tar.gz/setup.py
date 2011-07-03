#!/usr/bin/env python
import codecs

try:
    from setuptools import setup, find_packages
    from setuptools.command.test import test
except ImportError:
    raise
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command.test import test

long_description = codecs.open("README.rst", "r", "utf-8").read()

setup(
	name="cep",
	version="0.1",
	description="Pesquisa de CEPs via site dos Correios",
    author="Juarez Bochi",
	author_email="jbochi@gmail.com",
	url="https://github.com/jbochi/cep",
	platforms=["any"],
	license="MIT",
        packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
	install_requires=["BeautifulSoup"],
	tests_require=["nose"],
	test_suite="nose.collector",
	classifiers=[
		"Development Status :: 4 - Beta",
		"Operating System :: OS Independent",
		"Environment :: No Input/Output (Daemon)",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: Portuguese (Brazilian)",
		"Programming Language :: Python :: 2.5",
		"Programming Language :: Python :: 2.6",
		"Programming Language :: Python :: 2.7",
		"Topic :: Internet",
	],
	long_description=long_description
)
