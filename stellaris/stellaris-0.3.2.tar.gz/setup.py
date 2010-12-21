# -*- coding: iso-8859-15 -*-

try:
    from setuptools import setup, find_packages
except ImportError, e:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages    

setup(
    name = 'stellaris',
    version = '0.3.2',
    description = "Stellaris is a metadata management service.",
    author = "Mikael Hoegqvist",
    author_email = "hoegqvist@zib.de",
    maintainer = "Mikael Hoegqvist",
    maintainer_email = "hoegqvist@zib.de",
    url = "http://stellaris.zib.de/",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python", 
                   "Development Status :: 4 - Beta", 
                   "Operating System :: POSIX", "Topic :: Database :: Database Engines/Servers", 
                   "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"],
    long_description = """Stellaris is a metadata management service developed within the AstroGrid-D project. Our focus is to provide a flexible way to store and query metadata relevant for e-science and grid-computing. This can range from resource description of grid resources (compute clusters, robotic telescopes, etc.) to application specific job metadata or dataset annotations. We use common web-standards such as RDF to describe metadata and the accompanying query language SPARQL. Some features of the software include:

- A simple but powerful management interface for RDF-graphs
- Different backends for persistence through the use of RDFLib and Virtuoso
- Authorization and authentication based on X.509-certificates
- Supports different ways of VO-based authorization such as VOMRS
- SPARQL-protocol implementation with both XML/JSON result formats
""",
    
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    license="Apache License version 2.0",
    install_requires = [
    'stellaris.client >= 0.1.2',
    'benri >= 0.0.4',
    'rdflib == 2.4.0',
    'sqlalchemy >= 0.4.7',
    'authkit >= 0.4.0',
    'processing >= 0.51',
    'pexpect >= 2.3'
    ],
    scripts=['scripts/' + 'stellaris'],
    )
