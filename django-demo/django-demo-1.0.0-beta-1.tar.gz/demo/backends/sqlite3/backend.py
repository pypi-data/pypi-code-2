import os
import sqlite3

def drop(name):
    if os.path.exists(name):
        os.remove(name)
    else: # pragma: no cover
        pass
    
def create(name):
    sqlite3.connect(name).close()