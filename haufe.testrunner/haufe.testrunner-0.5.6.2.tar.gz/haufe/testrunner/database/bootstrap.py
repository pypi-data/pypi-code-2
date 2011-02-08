################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
################################################################

"""
Bootstrapping code
"""

import os
from optparse import OptionParser

from model import getModel
from config import WRAPPER_NAME
from setup import setup



def createTables(option, opt_str, value, parser):
    """ create the media database """

    Base, mappers = getModel(engine)    
    Base.metadata.create_all()


def createDatabase(option, opt_str, value, parser):
    """ low-level database creation """                

    url = engine.url
 
    cmd = 'dropdb --username %s --host %s %s' % (url.username, url.host, url.database) 
    os.system(cmd)

    cmd = 'createdb -E UNICODE --username %s --host %s %s' % (url.username, url.host, url.database)
    os.system(cmd)


def main():

    global engine

    dsn = os.environ.get('TESTING_DSN')
    if dsn is None:
        raise ValueError('$TESTING_DSN is undefined')

    engine = setup()
    parser = OptionParser()
    parser.add_option('-d', '--create-db', action='callback', callback=createDatabase,
                      help='(Re)create database')
    parser.add_option('-t', '--create-tables', action='callback', callback=createTables,
                      help='Create tables')

    options, args = parser.parse_args()    


if __name__ == '__main__':
    main()
