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
    "FlashMessage\n"
    "++++++++++++\n\n"
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
    name='FlashMessage',
    version=version,
    description="A pipe to set a message in a cookie so that on the next request it can be displayed on a web page without needing to persist the state in any more complex way.",
    long_description=long_description,
    # Get classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
       'Development Status :: 3 - Alpha',
       'License :: OSI Approved :: GNU Affero General Public License v3',
       'Programming Language :: Python :: 2',
       'Topic :: Software Development :: Libraries :: Python Modules',
       'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/flashmessage/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    extras_require={
        'test': [],
    },
    entry_points="""
    """,
)
