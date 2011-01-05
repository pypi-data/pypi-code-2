'''
========
TecUtils
========

TecUtils provides various utilities to accelerate development
of programs design to use MySQL as a database and substitute
the use of global variables.

TecUtils contains the following modules:

- mydb
- envvar

mydb
====

Requires:
    mysql-python
    
Provides:
    There are three functions that take care the database interaction:
    
    - GetRecordset(sHost,sUser,sPwd,sDB,sSQL)
    - GetData(sHost,sUser,sPwd,sDB,sSQL)
    - ExecuteSQL(sHost,sUser,sPwd,sDB,sSQL)
    
::
import TecUtils.mydb

myHost = "localhost"
myUser = "root"
myPwd = "password"
myDB = "test"


TecUtils.mydb.ExecuteSQL(myHost, myUser, myPwd, myDB, "INSERT INTO animal (name, category) VALUES " + \
    ('snake', 'reptile'), ('frog', 'amphibian'), ('tuna', 'fish'), ('racoon', 'mammal'), ('lizard', 'reptile')")
    
sql="SELECT name FROM animal WHERE category='reptile'"
TecUtils.mydb.GetRecordset(myHost, myUser, myPwd, myDB,sql)

thistype='fish'
sql="SELECT name FROM animal WHERE category='%s'" % thistype
TecUtils.mydb.GetData(myHost, myUser, myPwd, myDB,sql)
::

envvar
======

Provides:
    Reads a file containing <var>=<value> and loads in a container, so you can use container.var
    
    getVarFromFile(filename,container)

Use:
    
::
db = getVarFromFile('config/db.cfg','db')
::
    
Examples
--------

If use the two modules provides a way to use a configuration file to access de database:

::

# this is the config file:
# db.cfg
HOST = 'localhost'
USER = 'root'
PWD = 'ahivoy'
DB = 'facturae'

::

and use it in a program:

::
import TecUtils

TecUtils.envvar.getVarFromFile('db.cfg',db)

data = TecUtils.mydb.GetRecordset(db.HOST,db.USER,db.PWD,db.DB,"SELECT * FROM animal")
for animal in data:
    print animal[0]
    
::
'''