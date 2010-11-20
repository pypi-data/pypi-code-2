"""
Cloudlog controls the logging of all cloud related messages

Copyright (c) 2009 `PiCloud, Inc. <http://www.picloud.com>`_.  All rights reserved.

email: contact@picloud.com

The cloud package is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This package is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this package; if not, see 
http://www.gnu.org/licenses/lgpl-2.1.html
"""

import logging

from . import cloudconfig as cc

c = \
"""Filename where cloud log messages should be written.
This path is relative to ~/.picloud/"""
logFilename = cc.loggingConfigurable('log_filename',
                                     default='cloud.log',  #NOTE: will not create directories
                                     comment =c)
c = \
"""Should log_filename (default of cloud.log) be written with cloud log messages?
Note that cloud will always emit logging messages; this option controls if cloud should have its own log."""
saveLog = cc.loggingConfigurable('save_log',
                                 default=True,
                                 comment=c)
c = \
"""logging level for cloud messages.
This affects both messages saved to the cloud log file and sent through the python logging system.
See http://docs.python.org/library/logging.html for more information"""
logLevel = cc.loggingConfigurable('log_level',
                                  default=logging.getLevelName(logging.DEBUG),
                                  comment=c)

c = \
"""logging level for printing cloud log messages to console.
Must be equal or higher than log_level"""
printLogLevel = cc.loggingConfigurable('print_log_level',
                                  default=logging.getLevelName(logging.ERROR),
                                  comment=c)

datefmt = '%a %b %d %H:%M:%S %Y'

class NullHandler(logging.Handler):
    """A handler that does nothing"""
    def emit(self, record):
        pass


"""Initialize logging"""
def _initLogging():    
    import logging.handlers
    import os
    
    mylog = logging.getLogger("Cloud")
    
    #clear handlers if any exist
    handlers = mylog.handlers[:]
    for handler in handlers:
        mylog.removeHandler(handler)
        handler.close()
    
    if saveLog:
        from .util.cloghandler.cloghandler import ConcurrentRotatingFileHandler
        path = os.path.expanduser(cc.baselocation)
        try:
            os.makedirs(path)
        except OSError: #allowed to exist already
            pass
        path += logFilename
        
        try:
            handler = ConcurrentRotatingFileHandler(path,maxBytes=524288,backupCount=7)
        except Exception, e: #warn on any exception
            from warnings import warn
            warn('PiCloud cannot log to %s.  Error was %s' % (path, e))
            handler = NullHandler()
        else:
            #hack for SUDO user
            sudouid = os.environ.get('SUDO_UID')
            if sudouid:
                os.chown(path, int(sudouid),  int(os.environ.get('SUDO_GID')))
                os.chown(path.replace(".log","") + ".lock",int(sudouid),  int(os.environ.get('SUDO_GID')))
    else:
        #need a null hander
        handler = NullHandler()
    handler.setFormatter(logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(name)s: %(message)s", datefmt =datefmt))
    mylog.addHandler(handler)
    mylog.setLevel(logging.getLevelName(logLevel))    
    
    #start console logging:
    printhandler = logging.StreamHandler()
    printhandler.setLevel(logging.getLevelName(printLogLevel))
    printhandler.setFormatter(
       logging.Formatter("[%(asctime)s] - [%(levelname)s] - %(name)s: %(message)s",
       datefmt= datefmt))
    mylog.addHandler(printhandler)
    
    if saveLog and not isinstance(handler, NullHandler):
        mylog.debug("Log file (%s) opened" % handler.baseFilename)    
    return mylog
                                                              
cloudLog = _initLogging()                                     