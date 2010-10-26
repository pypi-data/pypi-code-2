"""
Distutils setup script for gerald. See http://halfcooked.com/code/gerald for
more information.
"""
__author__ = "Andrew J Todd esq. <andy47@halfcooked.com>"
__date__ = (2010, 2, 2)

from gerald import __version__
string_version = '.'.join([str(x) for x in __version__])

from setuptools import setup

setup(  name = "gerald",
        version = string_version,
        description = "Gerald database schema management utility",
        author = "Andrew J Todd esq.",
        author_email = "andy47@halfcooked.com",
        url = "http://halfcooked.com/code/gerald/",
        download_url = "http://pypi.python.org/pypi/gerald",
        py_modules = ['gerald',
                     ],
        packages = ['gerald.utilities',
                    'gerald.tests',
                    'gerald',
                   ],
        license = "BSD",
        long_description = """
Gerald is a general purpose toolkit written in Python for cataloguing, managing 
and deploying database schemas. Its major current use is to identify the 
differences between various versions of a schema. A schema is a single logical 
grouping of database objects usually made up of tables, views and stored code 
objects (functions and procedures).

You can use Gerald to determine the differences between your development and test 
environments, or to integrate changes from a number of different developers into 
your integration database.

Gerald is designed to be used in an Agile environment, but is useful regardless 
of your development methodology.

Gerald is designed from the ground up to support as many popular relational 
database systems as possible. Currently it will document and compare schemas 
from databases implemented in MySQL, Oracle and PostgreSQL. Other databases 
will be supported in future releases.""",
)
