#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


class UltraMagicString(object):
    '''
    Taken from
    http://stackoverflow.com/questions/1162338/whats-the-right-way-to-use-unicode-metadata-in-setup-py
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __unicode__(self):
        return self.value.decode('UTF-8')

    def __add__(self, other):
        return UltraMagicString(self.value + str(other))

    def split(self, *args, **kw):
        return self.value.split(*args, **kw)


long_description = UltraMagicString(u'\n\n'.join((
    file('README.rst').read(),
    file('CHANGES.rst').read(),
)))


setup(
    name = 'django-mockups',
    version = '0.4.1',
    url = 'https://github.com/sorl/django-mockups',
    license = 'BSD',
    description = 'Provides tools to auto generate content.',
    long_description = long_description,
    author = UltraMagicString('Mikko Hellsing'),
    author_email = 'mikko@aino.se',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages = [
        'mockups',
        'mockups.management',
        'mockups.management.commands'],
    install_requires = ['setuptools'],
    test_suite = 'runtests.runtests',
)
