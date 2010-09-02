try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.2.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "Psycopg2Database\n"
    "++++++++++++++++\n\n"
    ".. contents :: \n"
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
    name='Psycopg2Database',
    version=version,
    description="psycopg2 driver for the DatabasePipe package",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        #'Environment :: Web Environment',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/psycopg2database/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [
            "DatabasePipe>=2.2.0,<=2.2.99",
        ],
    },
    entry_points="""
        [database.engine]
        insert_record=psycopg2database.helper:postgresql_insert_record
        engine_name=psycopg2database:engine_name
        plugin_name=psycopg2database:plugin_name
        driver_name=psycopg2database:driver_name
        param_style=psycopg2database:param_style
        update_config=psycopg2database.helper:psycopg2_update_config
    """,
)
