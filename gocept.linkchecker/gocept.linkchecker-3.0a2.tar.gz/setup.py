# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 12305 2008-07-04 14:29:34Z zagy $

from setuptools import setup, find_packages


setup(
    name='gocept.linkchecker',
    version='3.0a2',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    description='Check links in your Plone site using a link monitoring server.',
    packages=find_packages('src'),
    package_dir={'':'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=['setuptools', 'lxml'],
)
