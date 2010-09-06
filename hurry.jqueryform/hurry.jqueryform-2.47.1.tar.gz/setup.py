from setuptools import setup, find_packages

JQUERY_FORM_VERSION = '2.47'
version = '2.47.1'

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
    name='hurry.jqueryform',
    version=version,
    description="hurry.resource style resources for jQuery Form Plugin.",
    long_description = long_description,
    classifiers=[],
    keywords='hurry.resource jquery',
    author='Martijn Faassen',
    author_email='faassen@startifact.com',
    license='MIT',
    packages=find_packages('src'),
    namespace_packages=['hurry'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'hurry.resource >= 0.10',
        'hurry.jquery',
        ],
    entry_points = {
        'hurry.resource.libraries': [
            'jqueryform = hurry.jqueryform:jqueryform_lib',
            ],
        },
    extras_require={
        'zopesupport': ['hurry.zoperesource'],
        },
    )
