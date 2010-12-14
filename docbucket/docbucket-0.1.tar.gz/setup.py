#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2010 Antoine Millet <antoine@inaps.org>
#
#       This file is part of DocBucket.
#       
#       Foobar is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       Foobar is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import os

ldesc = open(os.path.join(os.path.dirname(__file__), 'README')).read()

def flist(path):
	fl = os.listdir(path)
	return [os.path.join(path, f) for f in fl if os.path.isfile(f)]

setup(
    name='docbucket',
    version='0.1',
    description='A simple document manager for individuals written with Django',
    long_description=ldesc,
    keywords='django document mongodb',
    author='Antoine Millet',
    author_email='antoine@inaps.org',
    license='GPL3', 
    packages=find_packages(),
    #~ package_data={'docbucket': ['docbucket/templates/*']},
    #~ data_files=[('media/docbucket/css', flist('media/docbucket/css')),
                #~ ('media/docbucket/images', flist('media/docbucket/images')),
                #~ ('media/docbucket/js', flist('media/docbucket/js')),
                #~ ('media/docbucket/js/contrib', flist('media/docbucket/js/contrib'))],
    include_package_data=True,
    zip_safe=False,
    url='http://idevelop.org/p/docbucket/',
    classifiers=[
        'Programming Language :: Python',
    ],
)

