import os
import sqlite3

def drop(name):
    if os.path.exists(name):
        os.remove(name)
    
def create(name):
    sqlite3.connect(name).close()