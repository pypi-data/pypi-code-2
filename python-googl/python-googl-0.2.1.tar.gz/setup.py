# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

packages=find_packages()

setup(
    name='python-googl',
    version='0.2.1',
    description='Python goo.gl url shortener wrapper',
    author='Vince Spicer',
    author_email='vinces1979@gmail.com',
    url='http://code.google.com/p/python-googl',
    install_requires=[
        "httplib2",
        ],
    zip_safe=False,
    packages=packages,
    keywords=['google', 'url', 'googl'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]


)

