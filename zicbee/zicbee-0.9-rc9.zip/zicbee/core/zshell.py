""" Initialisation for zicbee (database init) """
# vim: et ts=4 sw=4
__all__ = ['songs', 'args', 'init']
import os
from zicbee.db import Database

#: default database name
DEFAULT_NAME='songs'

args = []

#: global :class:`~zicbee.db.dbe.Database` instance
songs = None

def init(args=None, db_name=None):
    """ Initialize zicbee
    Mostly useful to init the database
    """
    try:
        db
    except NameError:
        pass
    else:
        print "db cleanup"
        db.cleanup() # XXX: Ugly !
        db.close()

    db_name = db_name or os.environ.get('ZDB', DEFAULT_NAME)
    print "opening %s..."%db_name
    db = Database(db_name)
    globals().update( dict(songs=db, args=args) )

