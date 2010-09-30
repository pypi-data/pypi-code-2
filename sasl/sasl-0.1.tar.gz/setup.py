#!/usr/bin/env python
from setuptools import setup, Extension
from distutils.command.build_py import build_py

sasl_module = Extension('_saslwrapper',
                           sources=['sasl/saslwrapper.cpp', "sasl/saslwrapper.i"],
                           swig_opts=["-c++", "-python"],
                           include_dirs=["sasl"],
                           libraries=["sasl2"],
                           language="c++",
                           )

dist = setup (name = 'sasl',
       version = '0.1',
       url = "http://github.com/toddlipcon/python-sasl/tree/master",
       maintainer = "Todd Lipcon",
       maintainer_email = "todd@cloudera.com",
       description = """Cyrus-SASL bindings for Python""",
       ext_modules = [sasl_module],
       py_modules = ["sasl.saslwrapper"],
       include_package_data = True,
       # Necessary to workaround a distutils bug in earlier pythons:
       # http://mail.python.org/pipermail/distutils-sig/2005-November/005387.html
       options = { 'build_ext': {'swig_opts':'-c++'} }
       )

# Rerun the build_py to ensure that swig generated py is build
build_py = build_py(dist)
build_py.ensure_finalized()
build_py.run()

