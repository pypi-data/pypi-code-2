# encoding: utf-8
"""
__init__.py

Copyright (c) 2011, disko@binary-punks.com
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

 -  Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.
 -  Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.
 -  Neither the name of the binary punks nor the names of its contributors may
    be used to endorse or promote products derived from this software without
    specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import logging


# logging levels provided by Python's standard logging facility:

critical = logging.CRITICAL
error    = logging.ERROR
warning  = logging.WARNING
info     = logging.INFO
debug    = logging.DEBUG

VALID_THRESHOLDS      = ( critical,   error,   warning,   info,   debug)
VALID_THRESHOLD_NAMES = ("critical", "error", "warning", "info", "debug")

class InvalidThresholdException(ValueError):
    
    def __init__(self, threshold):
        
        msg = "Invalid threshold: '%s'. Must be one of: %s or None" % (threshold, ", ".join(VALID_THRESHOLD_NAMES))
        super(InvalidThresholdException, self).__init__(msg)
    


def _getLogger(name, console_threshold=None, logfile_threshold=None, logfile_path=None, console_format="%(levelname)s: %(name)s - %(message)s", logfile_format="%(asctime)s - %(levelname)s: %(name)s - %(message)s"):
    """return a configured Logger instance"""
    
    logger = logging.getLogger(name)
    
    # configure logging to console
    
    if console_threshold is not None:
        
        if console_threshold not in VALID_THRESHOLDS:
            raise InvalidThresholdException(console_threshold)
        
        ch = logging.StreamHandler()
        ch.setLevel(console_threshold)
        ch.setFormatter(logging.Formatter(console_format))
        logger.addHandler(ch)
    
    # configure logging to file
    
    if logfile_threshold is not None:
        
        if logfile_threshold not in VALID_THRESHOLDS:
            raise InvalidThresholdException(logfile_threshold)
        
        if logfile_path is None:
            raise ValueError("logfile_threshold=%s, logfile_path=None. Either specify the path to the file to log to, or set logfile_threshold to None." % logfile_threshold)
        
        fh = logging.FileHandler(logfile_path)
        fh.setLevel(logfile_threshold)
        fh.setFormatter(logging.Formatter(logfile_format))
        logger.addHandler(fh)
    
    # return the configured logger object
    
    return logger


# make "from bp.logging import *" work
getLogger = _getLogger
