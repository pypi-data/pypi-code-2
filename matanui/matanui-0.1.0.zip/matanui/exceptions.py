# -*- coding: utf-8 -*-
'''Exceptions for the MataNui server.'''

## Created: 2010-12-24 Guy K. Kloss <Guy.Kloss@aut.ac.nz>
##
## Copyright 2010 Guy K. Kloss
## Some rights reserved.
##
## http://www.aut.ac.nz/

__author__ = 'Guy K. Kloss <Guy.Kloss@aut.ac.nz>'

class MataNuiServiceException(Exception):
    """Exception raised by MataNui service."""
    
    def __init__(self, message, status):
        """
        Constructor.
        
        @param message: Error message for exception.
        @type message: C{str}
        @param status: HTTP return status, default is OK (C{int}, empty C{str})
            or giving a reason/explanation (C{int}, C(str})). In the case of 
            this exception, it will be populated by a non-OK status.
        @type status: C{tupel} of (C{int}, C(str}))
        """
        Exception.__init__(self)
        self.message = message
        self.status = status



class MataNuiStorerException(Exception):
    """Exception raised by storer backends."""
    
    def __init__(self, message):
        """
        Constructor.
        
        @param message: Error message for exception.
        @type message: C{str}
        """
        Exception.__init__(self)
        self.message = message



class MataNuiStorerNotFoundException(MataNuiStorerException):
    """Exception raised by storer backends if the requested resource is not found."""
