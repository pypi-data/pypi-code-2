from setuptools import setup, find_packages

import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )

setup(
    name='hurry.tinymce',
    version='3.3.9.4',
    description="TinyMCE for hurry.resource.",
    long_description=long_description,
    classifiers=[],
    keywords='',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource',
        ],
    entry_points= {
    'console_scripts': [
      'tinymceprepare = hurry.tinymce.prepare:main',
      ]
    },

    )
