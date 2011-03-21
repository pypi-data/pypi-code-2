#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages, setup

setup(
	name='django_qrcode_filter',
	version='0.0.1alpha',
	maintainer = "Zenobius Jiricek",
	maintainer_email = "airtonix@gmail.com",
	url="projects.airtonix.net/project/django-qrcode-filter",
	description = "Django application that provides simple template filter and tag to create inline datauri based images of qrcodes.",
	license='LICENSE.md',
	long_description=open('README.md').read(),
	packages=find_packages(exclude='tests'),
	include_package_data = True
)

