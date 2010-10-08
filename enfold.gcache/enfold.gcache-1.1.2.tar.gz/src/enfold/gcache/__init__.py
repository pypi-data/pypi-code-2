# $Id: __init__.py 4414 2010-10-08 15:24:18Z nikolay $
# Copyright: Enfold Systems, LLC

# NOTE: This 'getLogger' code is bogus.  EP uses a different log for each
# cache, so a global log doesn't make sense!
_logger = None

_logger = None
def getLogger():
    global _logger
    if _logger is None:
        # Use a default logger.
        import logging
        logging.basicConfig()
        _logger = logging.getLogger()
    return _logger

# The 'generic cache' interface
from cache import Cache, metadata, now, CacheProvider, CacheStorage
from cache import Uncachable, ValidationGotNewItem
from diskstorage import DiskStorage
