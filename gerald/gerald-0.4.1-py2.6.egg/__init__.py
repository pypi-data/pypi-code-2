"""
Gerald is a general purpose toolkit for managing and deploying database 
schemas. Its major current use is to identify the differences between 
various versions of a schema.

For more information see the web site at U{http://halfcooked.com/code/gerald}
"""
# Version number should follow PEP386
__version__ = (0, 4, 1)
try:
    from oracle_schema import Schema as OracleSchema
except ImportError:
    pass
try:
    from mysql_schema import Schema as MySQLSchema
except ImportError:
    pass
try:
    from postgres_schema import Schema as PostgresSchema
except ImportError:
    pass
