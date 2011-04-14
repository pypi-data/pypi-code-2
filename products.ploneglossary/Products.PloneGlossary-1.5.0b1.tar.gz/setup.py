from setuptools import setup, find_packages
import os

_home = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'Products', 'PloneGlossary')

version = open(os.path.join(_home, 'version.txt')).read().strip()

setup(
    name='Products.PloneGlossary',
    version=version,
    description="Hilite Plone content terms, mouserover shows the term definition as tooltip.",
    long_description=(open(os.path.join(_home, "README.txt")).read() +
                      "\n\n" +
                      open(os.path.join(_home, "CHANGES")).read()),
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='plone glossary',
    author='Ingeniweb',
    author_email='support@ingeniweb.com',
    url='http://plone.org/products/ploneglossary',
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
