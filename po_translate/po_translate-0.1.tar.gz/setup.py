# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

import version
    
setup(
    name='po_translate',
    version=version.__version__,
    description='A tool for translating .PO files by Google translate API',
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    url='http://bitbucket.org/victorlin/po_translate',
    license='MIT',
    install_requires=['polib'],
    py_modules=['version', 'po_translate'],
    entry_points = {
        'console_scripts': [ 
            'po_translate = po_translate:main',
            ]
        }
)
