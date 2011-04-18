try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup (
    name = 'nested_again',
    author = 'Taylor Etheredge',
    url = 'https://linuxedge@github.com/linuxedge/scripts.git',
    author_email = 'taylor.etheredge@gmail.com',
    version = '0.1',
    py_modules = ['nester'],
)

