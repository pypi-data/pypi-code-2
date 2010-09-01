try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "RedisPipe\n"
    "+++++++++\n\n"
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
    name='RedisPipe',
    version=version,
    description="A \"pipe\" to connect the Redis key value store to the WebPipes framework",
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
    author_email='james@<package hompage domain>',
    url='http://jimmyg.org/work/code/redispipe/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "redis==0.6.1",
        "PipeStack>=0.4.0,<0.4.99",
        "BareNecessities>=0.2.5,<0.2.99",
        "ConversionKit>=0.3.2,<0.3.99",
        "StringConvert>=0.3.0,<0.3.99",
    ],
    extras_require={
        'test': [],
    },
    entry_points="""
    """,
)
