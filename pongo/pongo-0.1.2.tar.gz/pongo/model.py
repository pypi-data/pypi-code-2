from pymongo import Connection
from config import conf

conn = None

def init_db():
    global conn
    conn = Connection(
        conf.get('mongodb', 'host'),
        conf.getint('mongodb', 'port'))

init_db()

