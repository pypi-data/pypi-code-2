import logging
from bn import AttributeDict
from databasepipe.helper import service_extensions

try:
    from conversionkit import Conversion
except ImportError:
    has_conversionkit = False
else:
    has_conversionkit = True

log = logging.getLogger(__name__)

#
# Database
#

class PerRequestConnectionCursor(object):
    def __init__(self, connection, cursor):
        self._connection = connection
        self._cursor = cursor
   
    def __getattr__(self, name):
        if name in ['execute', '_connection', '_cursor']:
            return self.__dict__[name]
        else:
            return getattr(self.__dict__['_cursor'], name)

    def execute(self, sql, values=()):
        log.info('Executing %r, %r', sql, values)
        converter = self._connection._execute_converter
        if converter:
            values = Conversion(values).perform(converter).result
        self._connection._should_commit = True
        return self._cursor.execute(sql, values)

    def fetchall(self, *k, **p):
        result = self._cursor.fetchall(*k, **p)
        log.debug('RESULT: %r', result)
        converter = self._connection._fetch_converter
        if converter:
            result = Conversion(AttributeDict(dict(cursor=self, result=result))).perform(converter).result
        return result

class PerRequestConnection(object):
    def __init__(
        self, 
        connection, 
        fetch_converter=None,
        execute_converter=None,
    ):
        self._connection = connection
        self._should_commit = False
        self._fetch_converter = fetch_converter
        self._execute_converter = execute_converter
        if not has_conversionkit:
            raise Exception(
                'Please install ConversionKit if you wish to use a database '
                'fetch converter'
            )

    def __getattr__(self, name):
        if name in [
            'cursor', 
            'close', 
            'commit', 
            'rollback', 
            '_connection', 
            '_should_commit',
        ]:
            return self.__dict__[name]
        else:
            return getattr(self.__dict__['_connection'], name)
   
    def cursor(self, *k, **p):
        return PerRequestConnectionCursor(
            self, 
            self._connection.cursor(*k, **p),
        )

    def rollback(self, *k, **p):
        self._should_commit = False
        return self._connection.rollback(*k, **p)
   
    def commit(self, *k, **p):
        self._should_commit = False
        return self._connection.commit(*k, **p)
   
    def close(self, *k, **p):
        self._should_commit = False
        result = self._connection.rollback()
        log.warning(
           'You shouldn\'t close the per-request database connection '
           'because other code executed during the request might need it, the '
           'instruction has been ignored and the connection is still open '
           'but the connection has been rolled back as it would have been if '
           'you really had closed the connection'
        )
        return result 


