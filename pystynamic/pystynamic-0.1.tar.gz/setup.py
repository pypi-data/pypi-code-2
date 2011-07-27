#!/usr/bin/env python

from setuptools import setup

setup(name='pystynamic',
      version='0.1',
      description='Python static website generator',
      author='Mark Hildreth',
      author_email='mark.k.hildreth@gmail.com',
      url='http://bitbucket.org/markhildreth/puzzle',
      packages=['pystynamic', 'pystynamic.commands'],
      scripts=['bin/pystynamic'],
     )
