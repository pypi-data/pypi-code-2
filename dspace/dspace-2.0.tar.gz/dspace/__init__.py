from logging import getLogger, Handler

from dspace.repository import Repository


try:
    from logging import NullHandler
except ImportError:
    class NullHandler(Handler):
        """ A 'no-op' log handler """
        def emit(self, record):
            pass

getLogger('dspace').addHandler(NullHandler())
