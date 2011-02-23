"""
System logger.

"""

import logging
import logging.handlers
import os
from dm.ioc import RequiredFeature
from dm.dictionarywords import *

def getLogger():
    """
    Convenience method to get instance of a python logger named after the
    application
    """
    dictionary = RequiredFeature('SystemDictionary')
    systemName = dictionary[SYSTEM_NAME]
    return logging.getLogger(systemName)
 
def initLogging():
    """
    Configure the logger system in code.
    Two loggers: root + application
    Two output sources: file + stderr
    Only log level at ERROR or above go to stderr
    Log level for output to file is configurable via logging.level (if this is
    mis-specified default to debug)
    """
    dictionary = RequiredFeature('SystemDictionary')
    logPath = os.path.abspath(dictionary[LOG_PATH])
    dirPath = os.path.dirname(logPath)
    if not os.path.exists(dirPath):
        os.makedirs(dirPath)
    logLevel = logging.INFO
    logLevels = {
        'DEBUG'    : logging.DEBUG,
        'INFO'     : logging.INFO,
        'WARNING'  : logging.WARNING,
        'ERROR'    : logging.ERROR,
        'CRITICAL' : logging.CRITICAL
    }
    logLevelName = dictionary[LOG_LEVEL].upper()
    if logLevelName in logLevels:
        logLevel = logLevels[logLevelName]
    elif logLevelName:
        raise Exception, "Logging level not in valid list: %s" % (
            " ".join(logLevels.keys())
        )
    
    consoleFormat = '%(name)s [%(levelname)s] %(message)s'
    consoleFormatter = logging.Formatter(consoleFormat)
    #fileFormat = '%(name)s:%(levelname)s %(module)s:%(lineno)d: %(message)s'
    fileFormat = '[%(asctime)s] %(message)s'
    fileFormatter = logging.Formatter(fileFormat)
    
    consoleHandler = logging.StreamHandler()
    # have to set level here since does not seem to work when set on logger
    consoleHandler.setLevel(logging.ERROR)
    fileHandler = logging.handlers.RotatingFileHandler(
        logPath,
        mode='a+',
        maxBytes=10000000,
        backupCount=5
    )
    consoleHandler.setFormatter(consoleFormatter)
    fileHandler.setFormatter(fileFormatter)
    fileHandler.setLevel(logLevel)
    
    rootLogger = logging.getLogger('')
    systemName = dictionary[SYSTEM_NAME]
    systemLogger = logging.getLogger(systemName)
    rootLogger.addHandler(consoleHandler)
    systemLogger.addHandler(fileHandler)
    # setting this level seems to have no effect
    # i.e. debug events from the application logger still get processed
    # so we have set level on handler above
    # rootLogger.setLevel(logging.ERROR)
    # still need to set this or we don't get anything below warning
    systemLogger.setLevel(logLevel)
    
initLogging()
log = getLogger()
log.info('Logger: Logging initialised.')

