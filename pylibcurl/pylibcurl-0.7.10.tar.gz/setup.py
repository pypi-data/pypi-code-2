#!/usr/bin/env python

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

version = '0.7.10'

setup(
    name='pylibcurl',
    version=version,
    description='python ctypes curl library',
    author='Askar Yusupov',
    author_email='devex.soft@gmail.com',
    url='http://bitbucket.org/jungle/pylibcurl',
    download_url='http://bitbucket.org/jungle/pylibcurl/downloads',
    license='MIT',
    packages=['pylibcurl'],
    keywords='curl ctypes',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ]
)

