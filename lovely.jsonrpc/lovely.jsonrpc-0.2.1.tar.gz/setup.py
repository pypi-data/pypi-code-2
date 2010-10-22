import os
from setuptools import setup, find_packages

longDesc = """

This package includes json-rpc client and server (wsgi) implementation.

"""

setup(
    name="lovely.jsonrpc",
    version="0.2.1",
    license = "Apache License 2.0",
    description = 'Python JSONRPC package',
    long_description = longDesc,
    keywords = "JSON RPC JSONRPC WSGI",
    author = "Lovely Systems GmbH",
    author_email = "bernddorn@gmail.com",
    url = 'http://code.google.com/p/lovely-jsonrpc',
    packages=find_packages('src'),
    package_dir = {'':'src'},
    zip_safe = True,
    include_package_data = False,
    platforms = ['Any'],
    namespace_packages = ['lovely'],
    install_requires = ['setuptools'],
    extras_require = dict(test=['zope.testing',
                                'simplejson',
                                'tornado',
                                'webtest']),
    )
