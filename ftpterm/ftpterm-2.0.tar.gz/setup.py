#!/usr/bin/python
#coding:utf-8

from distutils.core import setup

setup(
	name="ftpterm",
	author="Alice",
	author_email="alice.himmel.info@gmail.com",
	license="GPL",
	version="2.0",
	description="The Command Line Interface FTP Client.",
	py_modules=["main","setup","src.cli","src.command","src.redirect"],
	scripts=["ftpterm"]
)
