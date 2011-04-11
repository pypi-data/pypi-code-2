#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='d2to1',
    version='0.1',
    author='Erik M. Bray',
    author_email='embray@stsci.edu',
    description="Allows using distutils2-like setup.cfg files for a package's "
                "metadata with a distribute/setuptools setup.py",
    packages=['d2to1'],
    install_requires=['setuptools'],
    entry_points={
        'distutils.setup_keywords': ['d2to1 = d2to1.core:d2to1']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Setuptools Plugin',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
