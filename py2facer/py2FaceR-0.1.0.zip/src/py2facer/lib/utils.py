'''
Utils Module
============

Utiilties and Exceptions for py2TheFaceR
'''

license = ''' Copyright (C) 2011  <see AUTHORS file>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import argparse

class InvalidConfig(Exception):
    '''Invalid config options either from the ini file or the CLI
    '''
    
    pass

class InvalidState(Exception):
    '''Raised when the program gets into some kind of invalid state
    
    Examples: an invalid type, bad responses from flickr, corrupted files, etc. 
    '''
    
    pass

class ParseError(Exception):
    '''Raised when an error in parsing Picasa data is encountered.
    '''
    
    pass

class LogClassFilter(object):

    def __init__(self, name, invert=False):
        '''Pass/Filter all records at logger name "name"
        
        :param name: Name of the Logger to filter for. Name must be a full path.
        :type name: :obj:`str`
        :param invert: If true, allow only that Logger and it's children to 
            pass. (default: False)
        :type invert: Boolean
        '''
        
        self.name = name
        self.invert = invert
    
    def filter(self, record):
        '''Filters logger records based on the current internal state
        
        :param record: Logging record to filter
        :type record: :obj:`~logging.LogRecord`
        '''
        
        if record.name.startswith(self.name):
            return self.invert
        return not self.invert

# W0622 because it's bad form to override the name of vars from a library
#pylint: disable=W0622
class Incrementer(argparse.Action):
    
    def __init__(self, option_strings, dest, incr_by, default, nargs=None, 
                 const=None, type=None, choices=None, required=False, 
                 help=None, metavar=None):
        '''Monkeypatching the :class:`~argparse.Action.Incrementer` so it can
        support and arbitrary increment by. All other arguments are as in
        :class:`argparse.Action` with the exception of
        
        :param incr_by: The amount to increment by
        :type incr_by: :obj:`int` 
        '''
        
        super(Incrementer, self).__init__( option_strings=option_strings, 
                                           dest=dest, nargs=0, const=const, 
                                           default=default, required=required, 
                                           help=help)
        self.incr_by = incr_by

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, getattr(namespace, self.dest) + 
                self.incr_by)
        