try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.2.1'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "DreamweaverTemplate\n"
    "+++++++++++++++++++\n\n"
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
    name='DreamweaverTemplate',
    version=version,
    description="Parse Dreamweaver templates (.dwt files), includes a pipe to dynamically render templates.",
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
    url='http://jimmyg.org/work/code/dreamweavertemplate/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "BareNecessities>=0.2.5,<0.2.99",
    ],
    extras_require = {
        'test': [
            "pytidylib>=0.2.1,<=0.2.99",
        ]
    },
    entry_points="""
    """,
)
