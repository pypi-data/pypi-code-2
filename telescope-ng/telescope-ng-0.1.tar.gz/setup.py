from setuptools import setup, find_packages

setup(
    name='telescope-ng',
    version='0.1',
    keywords='rdf rdflib sparql orm',
    license='MIT',
    author="Brian Beck",
    description="RDF data mapper and SPARQL query builder (fork)",
    url='http://bitbucket.org/ww/telescope',
    packages=find_packages(),
    install_requires=['rdflib'],
    test_suite='nose.collector',
    tests_require=['nose']
)
