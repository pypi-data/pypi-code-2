#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import datetime
import os
import sys

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

class logger:

    levels = {CRITICAL: "CRITICAL",
              ERROR   : "ERROR",
              WARNING : "WARNING",
              INFO    : "INFO",
              DEBUG   : "DEBUG",
              NOTSET  : "NOTSET"}

    line_separator = '\n'

    max_file_size = 5000 * 1024
    
    def __init__(self, name, tee = False, log_dir = 'log'):
        self.filename = "%s.log" % os.path.join(log_dir, os.path.basename(name))
        self.datefmt = '%a, %d %b %Y %H:%M:%S'
        
        self.format = "[%(date)s] %(level)8s  %(message)s"
        
        self.file = file(self.filename, 'a')

        self.tee = tee

    def log(self, level, msg, *args, **kwargs):
        try:
            if (os.stat(self.filename).st_size > self.max_file_size):
                self._log_rotate()

            message = self.format % {'date'    : datetime.datetime.today().strftime(self.datefmt),
                                     'level'   : self.levels[level],
                                     'message' : (msg % args).encode('utf-8')}

            self.file.write(message + self.line_separator)
            self.file.flush()

            if (self.tee):
                print message
        except:
            print "Exception logging message"
            print "Exception: ", sys.exc_info()[1]
            print "Level: %s, message: %s" % (level, repr(msg))

    def _log_rotate(self):
        self.file.close()
        
        fmt = "%s.%%d" % self.filename
        i = 0
        while os.access(fmt % i, os.F_OK):
            i += 1

        os.rename(self.filename, fmt % i)
        self.file = file(self.filename, 'w')
        
        
    def debug(self, msg, *args, **kwargs):
        self.log(DEBUG, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.log(INFO, msg, *args, **kwargs)
        
    def warning(self, msg, *args, **kwargs):
        self.log(WARNING, msg, *args, **kwargs)
        
    def critical(self, msg, *args, **kwargs):
        self.log(CRITICAL, msg, *args, **kwargs)
        
    def error(self, msg, *args, **kwargs):
        self.log(ERROR, msg, *args, **kwargs)
        
        
