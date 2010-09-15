#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup
import tex as module

setup(
    name             = module.__name__,
    version          = module.__version__,
    description      = module.__doc__.split('\n')[0],
    long_description = '\n'.join(module.__doc__.split('\n')[1:]).strip('\n'),
    author           = module.__author__,
    author_email     = module.__author_email__,
    url              = module.__url__,
    py_modules       = [module.__name__],
    classifiers      = [c.strip() for c in module.__classifiers__.strip().split('\n')],
)
