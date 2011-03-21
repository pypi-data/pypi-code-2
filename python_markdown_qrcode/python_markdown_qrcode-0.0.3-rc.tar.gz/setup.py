#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages, setup

setup(
	name='python_markdown_qrcode',
	version='0.0.3-rc',
	maintainer="Zenobius Jiricek",
	maintainer_email="airtonix@gmail.com",
	url="projects.airtonix.net/project/markdown-qrcode",
	description='A markdown extension to insert qrcode datauri images based on supplied data.',
	license='LICENSE.md',
	long_description=open('README.md').read(),
	packages=find_packages(exclude='tests'),
	include_package_data = True
)

