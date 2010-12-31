""" 
Scrapy logging facility

See documentation in docs/topics/logging.rst
"""
import sys
import logging
import warnings

from twisted.python import log

import scrapy
from scrapy.conf import settings
from scrapy.utils.python import unicode_to_str
from scrapy.utils.misc import load_object

import scrapy.log

# Logging levels
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
SILENT = CRITICAL + 1

level_names = {
    logging.DEBUG: "DEBUG",
    logging.INFO: "INFO",
    logging.WARNING: "WARNING",
    logging.ERROR: "ERROR",
    logging.CRITICAL: "CRITICAL",
    SILENT: "SILENT",
}


class Scrapy01FileLogObserver(log.FileLogObserver):

    def __init__(self, f, level=INFO, encoding='utf-8'):
        self.level = level
        self.encoding = encoding
        self.subprocessing = settings['LOG_FILE']
        log.FileLogObserver.__init__(self, f)

    def emit(self, eventDict):
        ev = scrapy.log._adapt_eventdict(eventDict, self.level, self.encoding)
        if ev is not None:
            log.FileLogObserver.emit(self, ev)
            if ev['logLevel'] >= ERROR:
                msg = ev.get('message')
                if msg:
                    print ', '.join(msg)


def start(logfile=None, loglevel=None, logstdout=None):
    if scrapy.log.started or not settings.getbool('LOG_ENABLED'):
        return
    scrapy.log.started = True

    if log.defaultObserver: # check twisted log not already started
        loglevel = scrapy.log._get_log_level(loglevel)
        logfile = logfile or settings['LOG_FILE']
        file = open(logfile, 'a') if logfile else sys.stderr
        if logstdout is None:
            logstdout = settings.getbool('LOG_STDOUT')
        sflo = Scrapy01FileLogObserver(file, loglevel, settings['LOG_ENCODING'])
        _oldshowwarning = warnings.showwarning
        log.startLoggingWithObserver(sflo.emit, setStdout=logstdout)
        # restore warnings, wrongly silenced by Twisted
        warnings.showwarning = _oldshowwarning
        scrapy.log.msg("Scrapy %s started (bot: %s)" % (scrapy.__version__, \
            settings['BOT_NAME']))
