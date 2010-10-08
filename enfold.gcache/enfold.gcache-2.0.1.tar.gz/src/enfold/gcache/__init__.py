# $Id: __init__.py 4292 2010-08-30 19:57:37Z nikolay $
# Copyright: Enfold Systems, LLC

# NOTE: This 'getLogger' code is bogus.  EP uses a different log for each
# cache, so a global log doesn't make sense!
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
from utils import now
from cache import Cache, CacheStorage, metadata
from interfaces import Uncachable, ValidationGotNewItem
from diskstorage import DiskStorage
