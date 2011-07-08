# -*- coding: utf-8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

from os.path import dirname, abspath, join

version_file = join(abspath(dirname(__file__)), 'VERSION')
description_file = join(abspath(dirname(__file__)), 'README')

fd = open(version_file)
try:
    version = fd.readline().split('"')[1]
finally:
    fd.close()

fd = open(description_file)
try:
    description = fd.read()
finally:
    fd.close()

requires = [
        'pyyaml',
        'webob ==0.9',
        'ipaddr',
        'antlr_python_runtime',
        ]

setup(
    name="google-appengine",
    version=version,
    description="Google AppEngine (unofficial easy-installable version of AppEngine SDK)",
    long_description=description,
    author="Google",
    classifiers=["Development Status :: 1 - Planning",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: BSD License",
                "Programming Language :: Python",
                "Environment :: Web Environment",
                ],
    url="https://github.com/worrp/gae-sdk",
    license="Apache",
    download_url="http://pypi.python.org/packages/source/g/googleappengine/googleappengine-%s.tar.gz" % version,
    packages=find_packages(),
    #package_data={
    #    '': ['templates/*.*'],
    #    },
    #include_package_data=True,
    data_files=[
        ('templates', [
                'templates/logging_console_header.html',
                'templates/logging_console_footer.html',
                'templates/logging_console_middle.html',
                'templates/logging_console.js',
                ],
        ),
    ],
    install_requires=requires,
    scripts=[
        #'google/appengine/tools/dev_appserver_main.py',
        ],
      )
    
