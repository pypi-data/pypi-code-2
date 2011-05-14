"""Logging related stufff.

$Id: logger.py,v b0e8e4bd3d27 2011/05/14 17:42:19 seocam $"""
 
import logging
from imagescanner import settings

class CustomStreamHandler(logging.StreamHandler, object):
    def emit(self, record):
        record.msg = '%s: %s' % (record.levelname, record.msg)
        super(CustomStreamHandler, self).emit(record)

def config_logger():
    handler = CustomStreamHandler()
    logging.root.setLevel(settings.LOGGING_LEVEL)
    logging.root.addHandler(handler)
