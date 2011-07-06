try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys, os

version = '0.3.4'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    "ConversionKit\n"
    "+++++++++++++\n"
    "\n.. contents ::\n"
    "\n"+read('doc/index.txt')
    + '\n'
    + read('CHANGELOG.txt')
    + '\n'
    + 'License\n'
    + '=======\n'
    + read('LICENSE.txt')
    + '\n'
    'Download\n'
    '========\n'
)


setup(
    name='ConversionKit',
    version=version,
    description="A general purpose conversion library",
    long_description=long_description,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Environment :: Web Environment',
        'Environment :: Console',
    ],
    keywords='',
    author='James Gardner',
    author_email='',
    url='http://jimmyg.org/work/code/conversionkit/index.html',
    license='GNU AGPLv3',
    packages=find_packages(exclude=['ez_setup', 'example', 'test']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "BareNecessities>=0.2.3,<=0.2.99",
    ],
    extras_require = {
        'test': [
            "FormConvert>=0.3.0,<=0.3.99",
        ]
    },
    entry_points="""
    """,
)

