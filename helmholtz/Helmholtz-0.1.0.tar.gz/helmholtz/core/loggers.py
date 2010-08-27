#encoding:utf-8
import logging
from django.conf import settings

logging.HEADER = 60
logging.addLevelName(logging.HEADER, 'HEADER')

def logger_header(self, msg, *args, **kwargs):
    if self.manager.disable >= logging.HEADER:
        return
    if logging.HEADER >= self.getEffectiveLevel():
        apply(self._log, (logging.HEADER, msg, args), kwargs)
        
logging.Logger.header = logger_header
    
def create_console_handler():
    handler = logging.StreamHandler()
    handler.setLevel(logging.ERROR)
    handler.setFormatter(logging.Formatter('--[%(name)s]--[%(levelname)s]-- %(message)s'))
    return handler

def create_file_handler(location, mode):
    handler = logging.FileHandler(location, mode)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter('--[%(asctime)s]--[%(name)s]--[%(levelname)s]-- %(message)s'))
    return handler

def create_console(name):
    console_handler = create_console_handler()
    console = logging.getLogger(name)
    console.addHandler(console_handler)
    return console

def create_logger(name, mode):
    location = settings.LOGS_LOCATION + '/%s.log' % (name)
    file_handler = create_file_handler(location, mode)
    logger = logging.getLogger(name)
    logger.addHandler(file_handler)
    return logger

def create_mixed_logger(name, mode):
    location = settings.LOGS_LOCATION + '/%s.log' % (name)
    console_handler = create_console_handler()
    file_handler = create_file_handler(location, mode)
    mixed_logger = logging.getLogger(name)
    mixed_logger.addHandler(console_handler)
    mixed_logger.addHandler(file_handler)
    return mixed_logger
