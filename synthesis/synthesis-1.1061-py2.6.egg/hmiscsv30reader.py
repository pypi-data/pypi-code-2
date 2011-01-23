'''Reads a a set of HMIS CSV files into memory, parses their contents, and stores 
their informaton into a postgresql database.  This is a log database, so it holds 
everything and doesn't worry about deduplication.  The only thing it enforces 
are exportids, which must be unique.'''

import sys, os
from reader import Reader
from zope.interface import implements
from lxml import etree
from sqlalchemy.exceptions import IntegrityError
import dateutil.parser
#import logging
from conf import settings
import clsExceptions
import DBObjects
from fileUtils import fileUtilities
from errcatalog import catalog

class HmisCsv30Reader(DBObjects.databaseObjects):
    '''Implements reader interface.'''
    implements (Reader) 
    
    hmis_namespace = None 
    airs_namespace = None
    nsmap = None
    global FILEUTIL
    FILEUTIL = fileUtilities(settings.DEBUG, None)

    def __init__(self, dir_name):
        pass
        
if __name__ == "__main__":
    sys.exit(main()) 