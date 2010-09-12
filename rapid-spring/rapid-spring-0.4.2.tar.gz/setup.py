# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='rapid-spring',
    version='0.4.2',
    author='Tobi Vollebregt',
    author_email='tobivollebregt@gmail.com',
    packages=['rapid', 'rapid.unitsync'],
    scripts=['bin/rapid','bin/rapid-gui'],
    url='http://pypi.python.org/pypi/rapid-spring/',
    license='LICENSE.txt',
    description='spring content downloading',
    long_description=open('README.txt').read(),
    # running `setup.py sdist' gives a warning about this, but still
    # install_requires is the only thing that works with pip/easy_install...
    install_requires=['bitarray'],
)
