#!/usr/bin/env python
### -*- coding: utf-8 -*- #############################################
#######################################################################
from setuptools import setup, find_packages

setup(
    name='ng.skin.base',
    version='0.2.3',
    url='http://www.dreambot.ru/dreambotsite/ng.skin.base/',
    author='Andrey Orlov',
    author_email='dbdt@dreambot.ru',
    license='GPL v2.1',
    classifiers=['Environment :: Web Environment',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License (GPL)',
                 'Programming Language :: Python',
                 'Operating System :: OS Independent',
                 'Topic :: Internet :: WWW/HTTP',
                 'Framework :: Zope3',
                 ],
    description="Our basic skin: some macros, adapters and so on",
    long_description=(open('README.txt').read() + '\n\n' + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['ng','ng.skin'],
    include_package_data=True,
    install_requires=[x.strip() for x in open("DEPENDENCES.txt").read().split("\n") if x.strip()],
    zip_safe=False,
    )
