#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import sys
sys.path.insert(0, 'pyrg')
import pyrg

setup(
    name='pyrg',
    version=pyrg.__version__,
    description="Python UnitTest Result colorized tool.",
    long_description=open("README").read(),
    license='New BSD License',
    author='Hideo Hattori',
    author_email='hhatto.jp@gmail.com',
    url='http://www.hexacosa.net/project/pyrg/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Operating System :: Unix',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
    ],
    keywords="unittest colorize visualize",
    package_dir={'': 'pyrg'},
    py_modules=['pyrg'],
    zip_safe=False,
    entry_points={'console_scripts': ['pyrg = pyrg:main']},
)
