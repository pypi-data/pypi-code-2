'''
Created on 4 nov. 2010

@author: Arnaud
'''
import sqlite3
import os

def read():
    """Retrieve the stored bus stops
    """
    path = os.getcwd() + os.sep + "example.db"
    
    li = []
    if os.path.exists(path):
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("select * from bus_stops")
        li = []
        for bus_code, bus_name, bus_link in c:
            li.append([bus_name, bus_code, bus_link])
        c.close()
    return li

def save(bus_code, bus_name, bus_link):
    """Save a given bus stop
    """
    path = os.getcwd() + os.sep + "example.db"
    
    if not os.path.exists(path):
        conn = sqlite3.connect(path)

        c = conn.cursor()
        
        # Create table
        c.execute("""create table bus_stops
        (code text, name text, link text)""")
    else:
        #use existing DB
        conn = sqlite3.connect(path)

        c = conn.cursor()
    
    # Insert a row of data
    c.execute("insert into bus_stops values (?,?,?)", (bus_code, bus_name, bus_link))
    
    # Save (commit) the changes
    conn.commit()
    
    # We can also close the cursor if we are done with it
    c.close()
