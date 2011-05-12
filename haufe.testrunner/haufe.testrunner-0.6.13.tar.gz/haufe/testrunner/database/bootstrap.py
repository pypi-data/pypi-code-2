################################################################
# haufe.testrunner
#
# (C) 2007, 2008 Haufe Mediengruppe
################################################################

"""
Bootstrapping code
"""

import os
from optparse import OptionParser

from model import getModel
from config import WRAPPER_NAME
from setup import setup
from sqlalchemy.orm import create_session


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



def deleteTestrunner(option, opt_str, value, parser):
    """ Remove a testrunner by id including its associated 
        and results.
    """

    Base, mappers = getModel(engine)
    TR = mappers[0]
    session = create_session(engine)
    tr = session.query(TR).filter_by(id=value).one()
    session.delete(tr)
    session.flush()
    session.commit()
    print 'Testrunner deleted'

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
    parser.add_option('-x', '--delete-testrunner', action='callback', default=None, callback=deleteTestrunner,
                      type='int', help='Delete a testrunner by id')

    options, args = parser.parse_args()


if __name__ == '__main__':
    main()
