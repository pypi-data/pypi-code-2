#!/usr/bin/env python

from distutils.core import setup

setup(
    name='ultraconfig',
    version='0.2',
    description='A profile based YAML configuration library',
    author='Jason Reid',
    author_email='reid.jason@gmail.com',
    url='https://github.com/jreid42/ultraconfig',
    packages=['ultraconfig'],
    long_description="""\
    UltraConfig is a profile bases YAML configuration library for python.
    """,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
    ],
    keywords='profile yaml configuration',
    license="MIT",
    install_requires=[
        'setuptools',
        'PyYAML'
    ],
)
