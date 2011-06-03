# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys

sys.path.insert(0, 'src')
import book

version = book.__version__
name='book.isbn'
short_description = '`book.isbn` is a package for book ISBN.'
long_description= \
    open("README.rst").read()+ \
    open("CHANGES").read()

classifiers = [
    'Development Status :: 1 - Planning',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Topic :: Utilities',
    ]

setup(
    name='book.isbn',
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['book',],
    author='Tohru Ike',
    author_email='tohru.ike@gmail.com',
    url='http://pypi.python.org/pypi/book.isbn',
    license='NEW BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data = {'': ['buildout.cfg']},
    include_package_data=True,
    namespace_packages=['book'],
    zip_safe=False,
    install_requires=[
        'setuptools',
        ],
    extras_require=dict(
        test=[
            'Nose',
            'pep8',
        ],
    ),
    test_suite='nose.collector',
    tests_require=['Nose','pep8'],
    )
