import sys
import traceback
import logging

#
# Look for Pymunk
try:
    import pymunk
    pymunk.init_pymunk()
    PYMUNK_OK = True
except ImportError:
    import simplevecs as pymunk
    PYMUNK_OK = False
    
DETAIL = 5

class Filtering(logging.Filter):
    """A nice filtering formatter than can show certain types of log"""

    not_allowed = set([
    ])
    
    def filter(self, record):
        """Format the record"""
        return record.name not in self.not_allowed
        
filterer = Filtering()
log = logger = logging.getLogger('serge')
hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(relativeCreated)6d] :: %(levelname)7s %(name)20s :: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.addFilter(filterer)

def addFileLogging():
    """Add file logging"""
    global LOG_TO_FILE, fhdlr
    LOG_TO_FILE = True
    fhdlr = logging.FileHandler('log.txt', 'w')
    fhdlr.setFormatter(formatter)
    
#logger.setLevel(logging.DEBUG)
logger.setLevel(DETAIL)
#logger.setLevel(logging.ERROR)

def tb():
    """Return the traceback as a string"""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    return traceback.format_tb(exc_traceback)


class BaseError(Exception):
    """A useful base class for errors"""
    
    def __init__(self, text):
        """Initialialise and add traceback"""
        super(BaseError, self).__init__(text + '\n' + ''.join(tb()))

LOG_TO_FILE = False
        
def getLogger(name):
    """Return a new logger with the name"""
    l = logging.getLogger(name)
    l.addHandler(hdlr)
    l.setLevel(logger.level)
    l.addFilter(filterer)
    if LOG_TO_FILE:
        l.addHandler(fhdlr)

    return l


class Loggable(object):
    """A class that can log"""
    
    def addLogger(self):
        """Add a logger"""
        if 'log' not in self.__class__.__dict__:
            self.__class__.log = getLogger(self.__class__.__name__)

