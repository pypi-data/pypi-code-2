from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name = 'parameterized_testcase',
    version = '0.2',
    packages = find_packages(),

    # metadata for upload to PyPI
    author = 'Austin Bingham',
    author_email = 'austin.bingham@gmail.com',
    description = 'Create unittest-compatible parameterized testcases.',
    license = 'MIT',
    keywords = 'unittest',
    url = 'http://code.google.com/p/parameterized-testcase/',
    )

