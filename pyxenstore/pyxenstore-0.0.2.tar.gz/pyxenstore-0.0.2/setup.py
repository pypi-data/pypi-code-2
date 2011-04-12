#!/usr/bin/env python

from distutils.core import setup, Extension

package_dir = {'' : 'src'}

setup(name='pyxenstore',
    version='0.0.2',
    description='Python XenStore module',
    author='Chris Behrens',
    author_email='cbehrens@codestud.com',
    url='http://www.launchpad.net/pyxenstore/',
    license='Apache 2.0',
    ext_modules=[Extension('pyxenstore', ['src/pyxenstore.c'],
        include_dirs=['include'],
        depends=['include/pyxenstore.h'],
        libraries=['xenstore'],
        extra_compile_args=[])]
)
