# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging
"""
This module contains wrappers for the python logging-module.

The logger is accessed via:
log = logging.getLogger(logger_name)

"""

FORMAT = '%(asctime)s (%(levelname)s) %(name)s:%(module)s:%(message)s'

def get_logger(name):
    pass
    
def initLogger(logger_name, level=logging.INFO):
    """
    Initializes a logger for the given ``project``. Adds a StreamHandler
    to the logger.
    """

    log = logging.getLogger(logger_name)
    log.setLevel(level)
    
    # setup a basic stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(FORMAT))
    log.addHandler(stream_handler)

def changeLevel(logger_name, level):
    log = logging.getLogger(logger_name)
    log.setLevel(level)
    
def fileLogger(logger_name, filename):
    """
    Adds a file-logger to the given ``logger_name``.
    """
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(FORMAT)

    log = logging.getLogger(logger_name)
    log.addHandler(file_handler)    
