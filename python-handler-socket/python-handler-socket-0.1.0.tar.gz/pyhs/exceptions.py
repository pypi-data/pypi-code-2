"""Exceptions used with HandlerSocket client."""

class ConnectionError(Exception):
    """Raised on socket connection problems."""
    pass

class OperationalError(Exception):
    """Raised on client operation errors."""
    pass

class IndexedConnectionError(ConnectionError):
    """Raised on socket errors that happen with operations that have opened index."""
    pass
  