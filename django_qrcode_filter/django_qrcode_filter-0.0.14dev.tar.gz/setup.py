from distutils.core import setup
from setuptools import find_packages, setup

setup(
	name='django_qrcode_filter',
	version='0.0.14dev',
	maintainer = "Zenobius Jiricek",
	maintainer_email = "airtonix@gmail.com",
	url="projects.airtonix.net/project/django-qrcode-filter",
	description = "A simplet django application that provides a block and fitler templatetag to create inline DataURI based qrcode images.",
	license='LICENSE.md',
	packages=find_packages(exclude='tests'),
	include_package_data = True
)

