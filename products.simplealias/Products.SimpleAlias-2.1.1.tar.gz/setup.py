from setuptools import setup, find_packages
import os

def _textFromPath(*names):
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, *names)
    return open(path, 'r').read().strip()

version = _textFromPath('Products', 'SimpleAlias', 'version.txt')

long_description = (
    _textFromPath("Products", "SimpleAlias", "README.txt")
    + "\n\n"
    + _textFromPath("Products", "SimpleAlias", "CHANGES")
    + "\n")

setup(
    name='Products.SimpleAlias',
    version=version,
    description="SimpleAlias is a product that let's you create aliases or shortcuts to content somewhere in your Plone.",
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='web zope plone alias',
    author='Danny Bloemendaal',
    author_email='danny.bloemendaal@informaat.nl',
    url='http://plone.org/products/simplealias',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        ],
    entry_points="""
    # -*- Entry points: -*-
    """
    )
