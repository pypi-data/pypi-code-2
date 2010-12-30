# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

try:
    import version
    version = version.__version__
except ImportError:
    version = 'unknown'
    
setup(
    name='ex_loghandlers',
    version=version,
    description='A set of extended logging handlers',
    author='Victor Lin',
    author_email='bornstub@gmail.com',
    url='https://victorlin@bitbucket.org/victorlin/ex_loghandlers',
    license='MIT',
    py_modules=['version', 'ex_loghandlers'],
)
