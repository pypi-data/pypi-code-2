"""Setup for Products.ATCountryWidget package.
"""

import os.path
from setuptools import setup, find_packages

name = "Products.ATCountryWidget"
setup(
    name = name,
    version = "0.2.6",
    author = "Daniel Havlik",
    author_email = "dh@gocept.com",
    description = "A country widget for Archetypes",
    long_description = 
        open(os.path.join('README.txt')).read() +
        open(os.path.join('docs','CHANGES.txt')).read() + 
        open(os.path.join('docs','AUTHORS.txt')).read(),
    license = "ZPL 2.1",
    keywords = "archetypes plone",
    url='http://pypi.python.org/pypi/Products.ATCountryWidget',
    zip_safe=False,
    packages = find_packages('src'),
    include_package_data = True,
    package_dir = {'':'src'},
    namespace_packages = ['Products'],
    install_requires = ['setuptools'],
    )
