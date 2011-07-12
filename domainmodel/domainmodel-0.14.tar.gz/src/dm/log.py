"""
System logger.

"""

import logging
import logging.handlers
import os
from dm.ioc import RequiredFeature
from dm.dictionarywords import *

# Todo: Fix this up more.

def initLogging():
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
    
    #fileFormat = '%(name)s:%(levelname)s %(module)s:%(lineno)d: %(message)s'
    fileFormat = '[%(asctime)s] %(message)s'
    fileFormatter = logging.Formatter(fileFormat)
    
    fileHandler = logging.handlers.RotatingFileHandler(
        logPath,
        mode='a+',
        maxBytes=10000000,
        backupCount=5
    )
    fileHandler.setFormatter(fileFormatter)
    fileHandler.setLevel(logLevel)
    
    systemLogger = getLogger()
    systemLogger.addHandler(fileHandler)
    systemLogger.setLevel(logLevel)
    
def getLogger():
    dictionary = RequiredFeature('SystemDictionary')
    systemName = dictionary[SYSTEM_NAME]
    return logging.getLogger(systemName)
 
initLogging()
log = getLogger()
log.info('Logger: Logging initialised.')

