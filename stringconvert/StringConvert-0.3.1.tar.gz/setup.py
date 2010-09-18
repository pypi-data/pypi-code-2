try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.3.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "StringConvert\n"
    "+++++++++++++\n\n"
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
    name='StringConvert',
    version=version,
    description="Convert common objects to and from Python strings using ConversionKit",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/stringconvert/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "BareNecessities",
        "ConversionKit",
    ],
    extras_require = {
        'test': [
            "pydns>=2.3.3,<=2.3.99",
            "URLConvert>=0.3.0,<=0.3.100",
        ]
    },
    entry_points="""
    """,
)
