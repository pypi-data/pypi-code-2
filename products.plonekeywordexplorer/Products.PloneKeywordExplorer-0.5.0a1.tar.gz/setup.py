# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

def textOfFile(*path):
    return open(os.path.join(*path), 'r').read().strip()

version = textOfFile("Products", "PloneKeywordExplorer", "version.txt")

setup(
    name='Products.PloneKeywordExplorer',
    version=version,
    description="Explore Plone content by keywords/tags",
    long_description=(textOfFile("Products", "PloneKeywordExplorer", "README.txt")
                      + "\n\n"
                      + textOfFile("Products", "PloneKeywordExplorer", "CHANGES")),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone"
        ],
    keywords='plone keyword tag taxonomy navigation',
    author='Gilles Lenfant',
    author_email='gilles.lenfant@alterway.fr',
    url='http://svn.plone.org/svn/collective/',
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
    """,
    )
