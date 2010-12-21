# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import sys, logging

from logging.handlers import RotatingFileHandler

# this is taken from: http://wiki.python.org/moin/PythonDecoratorLibrary#head-d6f79f980db88e0bdf258e9c9e7d34ce37b43eee
# see the link for example

def Property(function):
    keys = 'fget', 'fset', 'fdel'
    func_locals = {'doc':function.__doc__}
    def probeFunc(frame, event, arg):
        if event == 'return':
            locals = frame.f_locals
            func_locals.update(dict((k,locals.get(k)) for k in keys))
            sys.settrace(None)
        return probeFunc
    sys.settrace(probeFunc)
    function()
    return property(**func_locals)
    

def id_generator():
    x = 1
    while True:
        yield x
        x += 1

def create_logger(log_id='stellaris', log_level='info', log_type='console', log_file=None):
    logger = logging.getLogger(log_id)
            
    if log_type == 'file' and log_file != None:
        # 1M/file and up to 10000 files
        hdlr = RotatingFileHandler(log_file, 'a', 2**20, 10000)
    # default is logging to stderr
    else:
        hdlr = logging.StreamHandler(sys.stderr)

    format = '[%(asctime)s - %(process)d:%(threadName)s] (%(levelname)s) %(module)s: %(message)s'
    formatter = logging.Formatter(format, '')
    hdlr.setFormatter(formatter)
    
    if not log_level in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
        log_level = 'WARNING'
                    
    logger.setLevel(getattr(logging, log_level))
    logger.addHandler(hdlr)
    
    return logger
