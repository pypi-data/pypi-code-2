from setuptools import setup, find_packages

from stat import ST_MTIME
import os
import os.path
import sys
from subprocess import Popen

import engage_django_sdk
from engage_django_sdk.version import VERSION



setup(
    name='engage-django-sdk',
    version=VERSION,
    author='genForma Corporation',
    author_email='support@genforma.com',
    packages=find_packages(),
    install_requires = [ "Django>=1.2", ],
    url='http://www.genforma.com',
    license='Apache V2.0',
    entry_points = {
        'console_scripts': [
            'engage-django-sdk = engage_django_sdk.__main__:main'
            ]},
    description='Engage SDK for Django',
    long_description=open('README.rst').read(),
    classifiers=[
    "Environment :: Console",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: POSIX",
    "Topic :: System :: Systems Administration"
    ],
)
