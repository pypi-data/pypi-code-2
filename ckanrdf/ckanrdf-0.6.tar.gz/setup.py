from setuptools import setup, find_packages
import sys, os

version = '0.6'
try:
    from mercurial import ui, hg, error
    repo = hg.repository(ui.ui(), ".")
    ver = repo[version]
except ImportError:
    pass
except error.RepoLookupError:
    tip = repo["tip"]
    version = version + ".%s.%s" % (tip.rev(), tip.hex()[:12])

setup(
    name='ckanrdf',
    version=version,
    description="CKAN Catalogue RDF Generation",
    long_description="""\
CKAN Catalogue RDF Generation""",
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='ckan rdf data catalogue',
    author='William Waites',
    author_email='ww@styx.org',
    url='',
    license='GPL',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "ckanclient",
        "ordf",
        ],
    entry_points="""
    [console_scripts]
    ckanrdf = ckanrdf.command:genrdf
    ckanlinks = ckanrdf.ckanlinks:ckanlinks
    corscheck = ckanrdf.corscheck:corscheck

    [ordf.namespace]
    ckanrdf = ckanrdf.namespace:init_ns

    """,
    )
