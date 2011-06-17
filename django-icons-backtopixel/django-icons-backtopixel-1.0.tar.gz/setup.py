#!/usr/bin/env python
from setuptools import setup
PACK_NAME = 'backtopixel'

setup(
    name = 'django-icons-' + PACK_NAME,
    version = '1.0',
    author = 'Mikhail Korobov',
    author_email = 'kmike84@gmail.com',
    url = 'http://bitbucket.org/kmike/django-icons/',
    description = PACK_NAME + ' icons pack for django.contrib.staticfiles',
    long_description = open('README.rst').read(),
    license = 'MIT license',

    packages=['icons_'+PACK_NAME],
    include_package_data = True,
    install_requires=['distribute'],

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
