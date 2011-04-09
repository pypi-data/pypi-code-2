# setup.py
#
#


"""
jsb.recipe.jsonbot
==================

`jsb.recipe.jsonbot` provides a series of `zc.buildout <http://pypi.python.org/pypi/zc.buildout>`_
recipes to help with `JSONBOT <http://code.google.com/jsb/>`_
development. 

:appfy.recipe.jsonbot\:install: Downloads JSONBOT libraries from PyPi and installs in
    the app directory.

Source code and issue tracker can be found at `http://code.google.com/p/jsb.recipe/ <http://code.google.com/p/jsb.recipe/>`_.

"""

## imports

import os
from setuptools import setup, find_packages

## get_readme function

def get_readme():
    base = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
    files = [
        os.path.join(base, 'README.txt'),
        os.path.join(base, 'CHANGES.txt'),
    ]
    content = []
    for filename in files:
        f = open(filename, 'r')
        content.append(f.read().strip())
        f.close()

    return '\n\n\n'.join(content)


setup(
    name='jsb.recipe.jsonbot',
    version='0.1a2',
    url='http://jsonbot.googlecode.com/',
    download_url="http://code.google.com/p/jsb-recipe/downloads",
    author='Bart Thate',
    author_email='bthate@gmail.com',
    description='The bot for you!',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'zc.buildout >= 1.4.3',
        'z3c.recipe.scripts',
    ],
    entry_points={
        'zc.buildout': [
            'default = jsb.recipe.jsonbot.install:Recipe',
        ],
    },
    zip_safe=False,
    keywords='buildout recipe jsonbot jsb zc.buildout ',
    long_description = """ JSONBOT is a remote event-driven framework for building bots that talk JSON to each other. This recipe can install jsonbot into a buildout environment. """,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',   
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: Other OS',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Software Development :: Libraries :: Python Modules'],
)
