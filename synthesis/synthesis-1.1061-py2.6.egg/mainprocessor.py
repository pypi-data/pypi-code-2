#!/usr/bin/env python

from synthesis.conf import settings
from synthesis import fileutils
from selector import FileHandler
import os
import sys
from synthesis.logger import Logger

class MainProcessor:
    def __init__(self):
        
        ###################################################################################
        # Looping construct
        # After that is done, we can enter our wait state for the arrival of new files.
        ###################################################################################
        
        # Display banner if in TEST Mode
        if settings.MODE == 'TEST':
            warningTxt = 'CAUTION: TEST MODE - This wipes DB Clean'
            fileutils.makeBlock(warningTxt)
            warningTxt = "CTRL-C or CTRL-Break to Stop - (waiting before startup, in case you don't want to wipe your existing db)"
            fileutils.makeBlock(warningTxt)
            # sleep for 10 seconds
            fileutils.sleep(1)
                
        # test if we are in debug and TEST Mode.  If so we clear out the DB every processing run, PROD mode need should never do this.
        if settings.DEBUG and settings.MODE == 'TEST':								# Only reset the DB in Test mode
            from synthesis import postgresutils
            utils = postgresutils.Utils()
            utils.blank_database()    
        
        # setup logging
        if not os.path.exists(settings.LOGS):
            os.mkdir(settings.LOGS)
        else:
            if settings.DEBUG:
                print "Logs Directory exists:", settings.LOGS
        
        # command argument set's log level or Settings.py
        if len(sys.argv) > 1:
            level = sys.argv[1]
        else:
            level = 0
        
        debugMessages = Logger(settings.LOGGING_INI, level)
        if settings.DEBUG:
            debugMessages.log("Logging System Online", 0)
            
        try:
            if settings.DEBUG:
                print "Now instantiating FileHandler"
            FileHandler() 
            print "calling sys.exit"
            sys.exit
        
        except KeyboardInterrupt:
            print 'Stopping: KeyboardInterrupt at MainProcessor.py'
            # need to shutdown the logging system prior to program termination.  This is to flush buffers, send messages etc.	
            debugMessages.__quit__()
            sys.exit()