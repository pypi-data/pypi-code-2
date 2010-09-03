try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.3.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "ErrorReport\n"
    "+++++++++++\n\n"
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
    name='ErrorReport',
    version=version,
    description="Provide HTML error reports during development of web applications and email reports for errors occurring in production.",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/errorreport/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [
            "PipeStack",
            "StringConvert",
            "RecordConvert",
        ],
    },
    entry_points="""
    """,
)
