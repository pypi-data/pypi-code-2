from setuptools import setup, find_packages
import sys, os

version = '0.1.1'

setup(
    name='osurf',
    version=version,
    description="ORDF - SurfRDF back-end",
    long_description="""\
Open Knowledge Foundation RDF Library - SurfRDF support""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Framework :: Paste",
        "Framework :: Pylons",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.6",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="rdf rdflib provenance messaging",
    author='Open Knowledge Foundation',
    author_email='okfn-help@lists.okfn.org',
    url="http://ordf.org/",
    license='AGPL',
    packages=["ordf"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "ordf",
        "surf",
        "surf.sparql_protocol",
    ],
    entry_points="""
        # -*- Entry points: -*-
        [ordf.handler]
        surf=ordf.osurf:Surf
    """,
)
