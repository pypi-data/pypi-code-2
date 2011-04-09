#!/usr/bin/env python
import os
from distutils.core import setup
from setuptools import find_packages, setup

here_path = os.path.abspath( os.path.join( os.path.dirname(__file__) ) )

setup(
	name='python_markdown_qrcode',
	version='0.0.5.1',
	maintainer="Zenobius Jiricek",
	maintainer_email="airtonix@gmail.com",
	url="projects.airtonix.net/project/markdown-qrcode",
	description='A markdown extension to insert qrcode datauri images based on supplied data.',
	license='LICENSE.md',
	long_description='README',
	packages=find_packages(exclude='tests'),
	include_package_data = True
)

