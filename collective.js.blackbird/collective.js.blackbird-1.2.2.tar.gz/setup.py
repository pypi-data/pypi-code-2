from setuptools import setup, find_packages
import os

version = '1.2.2'

setup(
    name='collective.js.blackbird',
    version=version,
    description="A Plone add-on package that provides Blackbird.js, an Open-Source Javascript logging utility.",
    long_description=open("README.txt").read() + "\n" +
                    open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
    "Programming Language :: Python",
    ],
    keywords='javascript logging plone blackbird',
    author='JC Brand for Syslab.com GmbH, Blackbird.js by G. Scott Olson',
    author_email='brand@syslab.com',
    url='http://www.gscottolson.com/blackbirdjs/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
