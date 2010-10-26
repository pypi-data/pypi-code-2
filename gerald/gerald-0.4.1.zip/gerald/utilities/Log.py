"""
Wrapper around the standard logging module to provide a simpler initiation and 
consistent formatting.
          
The differences from the standard are;
  - we always log to file
  - we use a standardised format
  - our default logging level is INFO, not WARN
  - the formatter does not include the log name '%(name)s' as we assume that each
    log is echoed to its own file
  - we do not append to the log file, rather we open the file for writing each 
    time. I may change this back to the default file access of 'a'

This module should really just contain a class which sub-classes of
logging.Logger. In the first instance we are nice and simple and 
just provide a function which returns the logger instance properly
set up.
"""
__author__ = "Andy Todd <andy47@halfcooked.com>"
__date__ = (2006, 3, 15)
__version__ = (1, 4, 0)

import logging

LOGS = {}

def get_log(log_name='', file_name=None, level='INFO'):
    """Instantiate log_name and make sure its output is written to file_name
    
    Set the (output) level according to the value of level
    If no file_name is provided then output should go to the screen
    """
    # We don't want to use the root logger so we will substitute 'default'
    if log_name == '':
        log_name = 'default'
    global LOGS
    if LOGS.has_key(log_name):
        return LOGS[log_name]
    else:
        # logging.basicConfig()
        log = logging.getLogger(log_name)
        log.setLevel(getattr(logging, level))
        # Define the handler and formmatter
        if file_name:
            handler = logging.FileHandler(file_name, "a")
        else:
            handler = logging.StreamHandler()
        # Attach the formatter to the handler and the handler to the log
        formatter = logging.Formatter("%(asctime)s %(levelname)s:: %(message)s","%Y.%m.%d %H:%M:%S")
        handler.setFormatter(formatter)
        log.addHandler(handler)
        LOGS[log_name] = log
        return log

def set_level(log_name, level):
    """Set the level on <log_name> to level

    See the standard documentation for the valid list of levels. They are
    all implemented as module attributes so we just use getattr
    """
    LOGS[log_name].setLevel(getattr(logging, level))
