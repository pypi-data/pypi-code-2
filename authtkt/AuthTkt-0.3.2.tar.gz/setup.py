try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.3.2'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "\n"+read('doc/index.txt')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    'License\n'
    '=======\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)

setup(
    name='AuthTkt',
    version=version,
    description="Python implementation of the mod_auth_tkt handler and Perl scripts",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
       'Development Status :: 3 - Alpha',
       'License :: OSI Approved :: Apache Software License',
       'Programming Language :: Python :: 2',
       'Topic :: Software Development :: Libraries :: Python Modules',
       'Topic :: System :: Systems Administration :: Authentication/Directory',
       'Environment :: Web Environment',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='',
    license='Apache 2.0',
    packages=find_packages(exclude=['example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [],
        'app': ['AppDispatch'],
    },
    entry_points="""
    """,
)
