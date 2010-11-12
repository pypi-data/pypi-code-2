from __future__ import with_statement
from demo.base import install_database
from django.db import connections
import MySQLdb
import time

username = connections.databases['default']['USER']
password = connections.databases['default']['PASSWORD']
host = connections.databases['default']['HOST']
port = connections.databases['default']['PORT'] or 3306


class Connection(object):
    def __enter__(self):
        self.con = MySQLdb.connect(user=username, passwd=password, host=host, port=port)
        self.cur = self.con.cursor()
        self.con.autocommit(True)
        return self.cur
    
    def __exit__(self, type, value, traceback): # pragma: no cover
        if not isinstance(value, Exception):
            self.con.commit()
        else:
            pass
        self.cur.close()
        self.con.close()

def drop(name):
    # needs to be installed so we can drop out of a request/response cycle
    install_database(name)
    connections[name].close()
    with Connection() as cur:
        time.sleep(1) # because of "is accessed by others" error
        cur.execute("DROP DATABASE IF EXISTS %s" % name)

def create(name):
    with Connection() as cur:
        cur.execute("CREATE DATABASE %s" % name)