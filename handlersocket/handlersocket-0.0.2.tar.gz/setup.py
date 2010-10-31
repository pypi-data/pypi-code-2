#!/usr/bin/env python

from setuptools import setup
import handlersocket

setup(name='handlersocket',
      version=handlersocket.version,
      packages=['handlersocket'],
      author='INADA Naoki',
      author_email='songofacandy@gmail.com',
      description='HandlerSocekt client for Python',
      long_description='HandlerSocekt is a NoSQL protocol for MySQL.\n' \
              'It is developed by DeNA.\n' \
              'This package provides client library for the protocol.\n',
      license='The MIT License',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Topic :: Database',
          ]
      )
