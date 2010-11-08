#!/usr/bin/env python

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

from pylibcurl import about

setup(
    name='pylibcurl',
    version=about.__version__,
    description='python ctypes curl library',
    author=about.__author__,
    author_email=about.__email__,
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

