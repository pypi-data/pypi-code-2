#!/usr/bin/env python

import logging 
from logging import config
from synthesis.borg import Borg

_defaultConfig = {}

class Logger(Borg):
    def __init__(self, configFile, loglevel=1):
        # make our class a singleton
        Borg.__init__(self)
        #print "Logging with INIFile from Logger: %s" % (configFile)
        
        self.LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
        
        try:
            config.fileConfig(configFile, _defaultConfig)
        except IOError:
            raise
        
        self.logger = logging.getLogger("synthesis.engine")
        self.logger.setLevel(loglevel)
        # test if logging dir exists, if not create it
        
    def getLogger(self, loggerName):
        return logging.getLogger(loggerName)
        
    def __quit__(self):
        print 'Shutting down logging system...'
        logging.shutdown()
    
    def log(self, message, loglevel=0):
        
        if loglevel == 0:
            self.logger.info(message)
        elif loglevel == 1:
            self.logger.debug(message)    
        elif loglevel == 2:
            self.logger.warning(message)    
        elif loglevel == 3:
            self.logger.error(message)
        elif loglevel == 4:
            self.logger.critical(message)
            
#if __name__ == "__main__":
#    
#    
#    # get the log level from the command line (args)
#    if len(sys.argv) > 1:
#        level = sys.argv[1]
#        #level = LEVELS.get(level_name, logging.NOTSET)
#    else:
#        level = logging.NOTSET
#        
#    myLog = Logger(configFile, level)
#    
#    #myLog._setConfig(level)
#    myLog.log(" Log Message", 0)
#    myLog.log(" Log Message", 1)
#    myLog.log(" Log Message", 2)
#    myLog.log(" Log Message", 3)
#    myLog.log(" Log Message", 4)
#    myLog.logger.critical("Test Debug")
#    
#    myLog2 = Logger()
#    myLog2.log(" Log2 Message", 4)
#    # Shutdown the logger
#    myLog.__quit__()
#        
