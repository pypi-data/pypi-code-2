#!/usr/bin/python

####################################################################################
#                                                                                  #
# Copyright (c) 2003 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
#                                                                                  #
# This file is part of Picalo.                                                     #
#                                                                                  #
# Picalo is free software; you can redistribute it and/or modify                   #
# it under the terms of the GNU General Public License as published by             #
# the Free Software Foundation; either version 2 of the License, or                # 
# (at your option) any later version.                                              #
#                                                                                  #
# Picalo is distributed in the hope that it will be useful,                        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                   #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                    #
# GNU General Public License for more details.                                     #
#                                                                                  #
# You should have received a copy of the GNU General Public License                #
# along with Foobar; if not, write to the Free Software                            #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA        #
#                                                                                  #
####################################################################################

import re, os, os.path, types, datetime, inspect, gzip, pickle
from picalo import Table, show_progress, clear_progress, check_valid_table, Date, DateTime, DateTimeFormat, number
import picalo

__doc__ = '''
  This module provides easy access to DB-API 2.0 tables.  It is a decorator
  for connections and cursors.  Cursor results can be accessed efficiently
  via field name or index.  
  
  Right now ODBC data sources are the primary mechanism to access databases.
  Set up ODBC in your operating system and call the OdbcConnection method
  to create a connection.  In addition, direct connections to MySQL and
  PostgreSQL are supported (without the need for an ODBC DSN setup).
  
  The primary use of this module is table(), which returns a standard
  Picalo table.  Other methods are provided for 
  advanced users who want more control over the databse connection.
  
  Most users only need to learn how to 1) create Connection objects,
  and 2) run conn.table() to query database tables.
       
  The module also provides classes to ease the creation of insert, update, and
  select queries.  
'''
  
__functions__ = (
  'SqliteConnection',
  'OdbcConnection',
  'PostgreSQLConnection',
  'PyGreSQLConnection',
  'MySQLConnection',
  'OracleConnection',
)



##############################################
###   The connection functions


def SqliteConnection(dirname):
  '''Opens a database connection to an SQLite database using the built-in
     sqlite3 driver.  SQLite is a lightweight, disk-based database that 
     doesn't require a separate server.  It is an excellent choice for small
     applications where you want to use SQL but don't need a "real" database
     like MySQL, PostgreSQL, or Oracle.  Since it comes with Picalo, it's
     ready to go immediately -- nothing is required except a Picalo install.
     
     @param    dirname:  The directory to store database files in, or ":memory:" to keep everything in memory.
     @type     dirname:  str
     @returns: A database connection.
     @rtype:   _Connection
  '''
  assert isinstance(dirname, types.StringTypes), 'Invalid directory name: ' + str(dirname)
  func_args = {
    'dirname': dirname,
  }
  import sqlite3
  db = sqlite3.connect(dirname)
  return _SqliteConnection(db, 'SqliteConnection', func_args)


def OdbcConnection(dsn_name, username=None, password=None):
  '''Opens a database connection to an ODBC database using
     the PyODBC driver.  
     
     @param    dsn_name: The DSN string to your database (as defined in the control panel)
     @type     dsn_name: str
     @param    username: Your username for the connection
     @type     username: str
     @param    password: Your password for the connection
     @type     password: str
     @returns: A database connection.
     @rtype:   _Connection
  '''
  assert isinstance(dsn_name, types.StringTypes), 'Invalid DSN name: ' + str(dsn_name)
  assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
  assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
  func_args = {
    'dsn_name': dsn_name,
    'username': username,
    'password': password,
  }
  dsn = 'DSN=%s' % (dsn_name, )
  if username != None and password != None:
    dsn = 'DSN=%s;UID=%s;PWD=%s' % (dsn_name, username, password)
  elif password != None:
    dsn = 'DSN=%s;PWD=%s' % (dsn_name, password)
  import pyodbc
  db = pyodbc.connect(dsn)
  return _OdbcConnection(db, 'OdbcConnection', func_args)


def PostgreSQLConnection(database, username=None, password=None, host=None, port=None):
  '''Opens a database connection to a PostgreSQL database using
     the psycopg2 driver.
     
     @param    database: The database name to connect to.
     @type     database: str
     @param    username: Your username for the connection.
     @type     username: str
     @param    password: Your password for the connection.
     @type     password: str
     @param    host:     The server hostname or IP address.
     @type     host:     str
     @param    port:     The server port to connect on.
     @type     port:     int
     @returns: A database connection.
     @rtype:   _Connection
  '''
  assert isinstance(database, types.StringTypes), 'Invalid database name: ' + str(database)
  assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
  assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
  assert isinstance(host, (types.StringTypes, types.NoneType)), 'Invalid host name or IP address: ' + str(host)
  if isinstance(port, types.StringTypes):
    port = int(port)
  assert isinstance(port, (types.IntType, types.NoneType)), 'Invalid port: ' + str(port)
  func_args = {
    'database': database,
    'username': username,
    'password': password,
    'host':     host,
    'port':     port,
  }
  args = []
  args.append('dbname=%s' % (database, ))
  if username != None: args.append('user=%s' % (username, ))
  if password != None: args.append('password=%s' % (password, ))
  if host != None: args.append('host=%s' % (host, ))
  if port != None: args.append('port=%s' % (port, ))
  dsn = ' '.join(args)
  import psycopg2
  db = psycopg2.connect(dsn)
  return _Psycopg2Connection(db, 'PostgreSQLConnection', func_args)


def PyGreSQLConnection(database, username=None, password=None, host=None, port=None):
    '''Opens a database connection to a PostgreSQL database using
       the PyGreSQL driver.

       @param    database: The database name to connect to.
       @type     database: str
       @param    username: Your username for the connection.
       @type     username: str
       @param    password: Your password for the connection.
       @type     password: str
       @param    host:     The server hostname or IP address.
       @type     host:     str
       @param    port:     The server port to connect on.
       @type     port:     int
       @returns: A database connection.
       @rtype:   _Connection
    '''
    assert isinstance(database, types.StringTypes), 'Invalid database name: ' + str(database)
    assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
    assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
    assert isinstance(host, (types.StringTypes, types.NoneType)), 'Invalid host name or IP address: ' + str(host)
    if isinstance(port, types.StringTypes):
      port = int(port)
    assert isinstance(port, (types.IntType, types.NoneType)), 'Invalid port: ' + str(port)
    func_args = {
      'database': database,
      'username': username,
      'password': password,
      'host':     host,
      'port':     port,
    }
    args = {}
    args['database'] = database
    if username != None: args['user'] = username
    if password != None: args['password'] = password
    if host != None: 
      args['host'] = host
    else:
      args['host'] = 'localhost'
    if port != None: args['host'] += ':' + str(port)
    import pgdb
    db = pgdb.connect(**args)
    return _PyGreSQLConnection(db, 'PyGreSQLConnection', func_args)


def MySQLConnection(database, username=None, password=None, host=None, port=None):
  '''Opens a database connection to a MySQL database using
     the MySQLdb driver.
     
     @param    database: The database name to connect to.
     @type     database: str
     @param    username: Your username for the connection.
     @type     username: str
     @param    password: Your password for the connection.
     @type     password: str
     @param    host:     The server hostname or IP address.
     @type     host:     str
     @param    port:     The server port to connect on.
     @type     port:     int
     @returns: A database connection.
     @rtype:   _Connection
  '''
  assert isinstance(database, types.StringTypes), 'Invalid database name: ' + str(database)
  assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
  assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
  assert isinstance(host, (types.StringTypes, types.NoneType)), 'Invalid host name or IP address: ' + str(host)
  if isinstance(port, types.StringTypes):
    port = int(port)
  assert isinstance(port, (types.IntType, types.NoneType)), 'Invalid port: ' + str(port)
  func_args = {
    'database': database,
    'username': username,
    'password': password,
    'host':     host,
    'port':     port,
  }
  args = {}
  args['db'] = database
  if username != None: args['user'] = username
  if password != None: args['passwd'] = password
  if host != None: args['host'] = host
  if port != None: args['port'] = port
  import MySQLdb
  db = MySQLdb.connect(**args)
  return _MySQLdbConnection(db, 'MySQLConnection', func_args)



def OracleConnection(dsn, username=None, password=None):
  '''Opens a database connection to an Oracle database using
     the cx_Oracle driver.  
     
     @param    dsn: The DSN string to your database
     @type     dsn: str
     @param    username: Your username for the connection
     @type     username: str
     @param    password: Your password for the connection
     @type     password: str
     @returns: A database connection.
     @rtype:   _Connection
  '''
  assert isinstance(dsn, types.StringTypes), 'Invalid DSN: ' + str(dsn)
  assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
  assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
  func_args = {
    'dsn': dsn,
    'username': username,
    'password': password,
  }
  import cx_Oracle
  db = cx_Oracle.connect(username, password, dsn)
  return _OracleConnection(db, 'OracleConnection', func_args)



################################################################################
###   Private methods and classes in the module:                             ###
################################################################################




###################################################
###   The main database connection decorator
###   If we don't have a specialized subclass
###   for the a given database driver, this
###   superclass is used.


class _Connection(picalo.AbstractDecorator):
  '''The base class of connections'''
  
  QUERY_PARAMETER = '%s'    # the string used for parameters in queries
  
  def __init__(self, dbconnection, connect_func, connect_args):
    assert hasattr(dbconnection, 'cursor'), 'Invalid database connection: ' + str(dbconnection)
    assert hasattr(dbconnection, 'commit'), 'Invalid database connection: ' + str(dbconnection)
    picalo.AbstractDecorator.__init__(self, dbconnection)
    self._table_cache = {}   # cache to hold tables automatically loaded from the database
    self._connect_func = connect_func
    self._connect_args = connect_args
    self.filename = None
    self.modified = True
    
    
  def __getattr__(self, key):
    '''Returns the given attribute of the class.  In addition, you can type
       connection.table to access any table in the database.  The connection
       will automatically "SELECT * FROM table" and pull the records in an
       efficient way as you need them.
    '''
    # first try me and my super
    try: 
      return picalo.AbstractDecorator.__getattr__(self, key)     # first priority is this object
    except AttributeError: 
      try:
        return self.__dict__['_table_cache'][key]  # see if we already loaded this table
      except KeyError:
        useProgress = picalo.useProgress
        picalo.useProgress = False
        try:
          if key in self.list_tables():
            table = self.table("SELECT * FROM " + key) # load the table and store in the cache
            self.__dict__['_table_cache'][key] = table
            return table
          raise AttributeError, "object has no attribute '%s'" % (key, )
        finally:
          picalo.useProgress = useProgress
          
          
  def is_changed(self):
    '''Returns whether the connection needs saving'''
    return self.modified
              
          
  def refresh(self, tablename=None):
    '''Refreshes the given table name, if it has already been pulled
       from the database.  This has relation to the db.tablename syntax.  If the table
       has been updated on the database, we won't pull the new records until
       this method is called.  When tablename is None, all tables are refreshed.
       
       @param tablename:  The relation name to refresh, None to refresh all tables in this database.
       @type tablename:  str
    '''
    if tablename == None:    # refresh everything
      self.__dict__['_table_cache'] = {}
    else:                    # refresh a single table
      if self.__dict__['_table_cache'].has_key(tablename):
        del self.__dict__['_table_cache'][tablename]
          
  
  def cursor(self):
    '''Returns a cursor to the database.  Since Picalo manages cursors automatically,
       most users don't need to access them directly.   The method is provided for
       advanced users who want to explicitly manage cursors.
       
       @return:    A cursor to the database.
       @rtype:     _Cursor
    '''
    return _Cursor(self, self._decorated_object.cursor())
    
    
  def execute(self, sql, parameters=None, close_cursor=True):
    '''Runs executable queries (INSERT, UPDATE, DELETE) that don't 
       return tables.  This is the primary methods to use when posting information
       to a database.
       
       IMPORTANT: Since most databases don't commit changes automatically, you *must* call 
       commit() to make the changes permanent.  If you close the connection without
       committing, you'll lose all of your changes.
       
       Alternatively, you can call rollback() to undo all changes since the last commit()
       call.
       
       Example:
         >>> myconn.execute("CREATE TABLE mytable (id integer, name varchar(20))")
         >>> myconn.execute("INSERT INTO mytable (id, name) VALUES (1, 'Dennis')")
         >>> myconn.commit()
       
       @param sql:           The SQL string to execute.
       @type  sql:           string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @param close_cursor:  Determines whether the cursor is closed automatically.  Unless you need the cursor for something else, you should allow it to close automatically.
       @type  close_cursor:  bool
       @return:              The return value from the database.  This varies from database to database and is probably not very useful.  If errors occur in the operation, exceptions are thrown.
       @rtype:               object
    '''
    # types are checked in cursor.execute
    cursor = self.cursor()
    try:
      if parameters != None:
        ret = cursor.execute(sql, parameters)
      else:
        ret = cursor.execute(sql)
    finally:
      if close_cursor:
        cursor.close()
    return ret
    
  
  def commit(self):
    '''Commits any changes to the database.  If you make modifications of any
       kind to your database tables (INSERT, UPDATE, CREATE, etc.), you *must*
       commit those changes by calling commit().
       
       If you close a database connection without committing, you'll lose all
       changes.
       
       Analyses that only run SELECT calls on a database do not need to commit().
       
       See the execute() method for an example of committing.
    '''
    self._decorated_object.commit()
    

  def query(self, sql, parameters=None):
    '''Runs a SELECT query that returns a result set.  This method provides
       efficient access to extremely large data sets, but it is not as easy to
       use as table().  Most users should use table() unless you explicitly need to
       access only one record at a time. In other words, check out 
       Database.Connection.table(sql) and use it unless you really need
       the efficiency offered by this method.
       
       Stated differently, query() and table() accomplish the same task:
       query a database.  The query() method is more efficient and the table()
       method is more powerful and easier to use.
       
       If you need to efficiently use memory and must use this method, you should use an
       iterator in a for loop as is done in the example.  This allows you
       to access one record at a time.  Note that you can only go in forward
       direction one at a time.  If you need to go backwards in your analysis,
       either store the records in variables or use table().
       
       Example:
         >>> import psycopg
         >>> myconn = Database.Connection(psycopg.connect(database='mydb'))
         >>> for record in myconn.query("SELECT * FROM mytable"):
         ...   print record['id']
         ...   print record['name']
         ...
         1
         Dennis
       
       @param sql:  The SQL string to execute.
       @type  sql:  string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @return:     A cursor to the result set.
       @rtype:      Cursor
    '''
    # types are checked in cursor.query
    return self.cursor().query(sql, parameters)
    

  def query1(self, sql, parameters=None):
    '''Runs a SELECT query and returns only the first record from the result set.
       There are many times when you expect only a single record in the result
       set, such a key value query.  In these circumstances, query1() provides
       easy access directly to the first record.
       
       The method returns a single Record instance or None if no results are found.

       Example:
         >>> import psycopg
         >>> myconn = Database.Connection(psycopg.connect(database='mydb'))
         >>> rec = myconn.query1("SELECT min(id) FROM mytable")
         >>> print rec
         1
       
       @param sql:  The SQL string to execute.
       @type  sql:  string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @return:     A single result set record.
       @rtype:      Record
    '''
    # types are checked in cursor.query1
    return self.cursor().query1(sql, parameters)

    
  def table(self, sql, parameters=None):
    '''This method is the primary access to databases within Picalo.  Most users will create
       a connection and then call only this method to retrieve data from tables.
    
       Retrieves a Table to the results of a new query or the most recently-run query.
       Table objects have additional methods not found in this module, such as
       pretty printing, saving to text files, and mutability.  
       
       If your database driver is one of the enhanced support drivers (such as 
       PythonWin's odbc, psycopg, and MySQLdb drivers), the method will automatically
       set column types.
       
       The primary reason you would not want to use this method is that it loads
       all records into memory at query time, so it might use up your memory
       with super large tables.       
       Example:
        >>> import psycopg
        >>> myconn = Database.Connection(psycopg.connect(database='conan'))
        >>> data = myconn.table("SELECT * FROM mytable")
        >>> data.view()
        +----+--------+
        | id |  name  |
        +----+--------+
        |  1 | Dennis |
        +----+--------+
        
       @param sql:   The SQL string to execute.
       @type  sql:   string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @return:      A picalo table containing the results.
       @rtype:       Table
    '''
    # types are checked in cursor.table
    return self.cursor().table(sql, parameters)
    
    
  def insert_query_builder(self, tablename):
    '''This method returns a helper class for creating INSERT queries.
       It allows you to create INSERT queries piece by piece and is 
       available for advanced users.  It is useful when creating an SQL
       query programatically in a script.
    
       Example:
       >>> db = Database.PostgreSQLConnection('mydb')
       >>> q = db.insert_query_builder('test')
       >>> q.add('id', 5)
       >>> q.add('name', 'Sally')
       >>> print q
       QueryBuilder: <cursor>.execute("INSERT INTO test (id, name) VALUES (%s, %s)", [5, 'Sally'])
       >>> q.execute()
       >>> db.commit()

       @param tablename:   The database table name to insert the records into
       @type  tablename:   str
       @return:            An InsertQueryBuilder object.  
       @rtype:             InsertQueryBuilder
    '''
    assert isinstance(tablename, types.StringTypes), 'Invalid table name: ' + str(tablename)
    return InsertQueryBuilder(tablename, self)
    
    
  def update_query_builder(self, tablename):
    '''This method returns a helper class for creating simple UPDATE queries.
       It allows you to create UPDATE queries piece by piece and is 
       available for advanced users.  It is useful when creating an SQL
       query programatically in a script.

       Example:    
       >>> db = Database.PostgreSQLConnection('mydb')
       >>> q = db.update_query_builder('test')
       >>> q.add_where('id', 3)
       >>> q.add('name', 'newname')
       >>> print q
       QueryBuilder: <cursor>.execute("UPDATE test SET name=%s WHERE id=%s", ['newname', 3])
       >>> q.execute()     
       >>> db.commit() 
       
       @param tablename:   The database table name to update the records in.
       @type  tablename:   str
       @return:            An UpdateQueryBuilder object.  
       @rtype:             UpdateQueryBuilder
    '''
    assert isinstance(tablename, types.StringTypes), 'Invalid table name: ' + str(tablename)
    return UpdateQueryBuilder(tablename, self)
  
  
  def select_query_builder(self, tablename, select_fields=["*"]):
    '''This method returns a helper class for creating simple SELECT queries.
       It allows you to create SELECT queries piece by piece and is 
       available for advanced users.  It is useful when creating an SQL
       query programatically in a script.

       Example:    
       >>> db = Database.PostgreSQLConnection('mydb')
       >>> q = db.select_query_builder('test', ['id', 'name'])
       >>> q.add_where('id', 1)
       >>> print q
       QueryBuilder: <cursor>.execute("SELECT id, name FROM test WHERE id=%s", [1])
       >>> results = q.table()
       >>> results.prettyprint()
       +----+--------+
       | id |  name  |
       +----+--------+
       |  1 | Joseph |
       +----+--------+

       @param tablename:     The database table name to update the records in.
       @type  tablename:     str
       @param select_fields: The fields to be selected by the query.
       @type  select_fields: list or tuple of strings
       @return:              An SelectQueryBuilder object.  
       @rtype:               SelectQueryBuilder
    '''
    assert isinstance(tablename, types.StringTypes), 'Invalid table name: ' + str(tablename)
    return SelectQueryBuilder(tablename, select_fields, self)
 
 
  def _create_database_table(self, table, name, replace=False):
    '''Creates a databaes relation matching the column names and types
       of the given table.'''
    check_valid_table(table)
    assert isinstance(name, types.StringTypes), 'Invalid table name: ' + str(name)
    # try to drop the table if it exists and the user asked for replace
    if replace:
      try:
        try:
          cursor = self.cursor()
          cursor.execute('DROP TABLE ' + name)
        finally:
          cursor.close()
      except:  # if the table doesn't exist, we get an error
        pass
    self.commit()  # end the current transaction, just in case we had a failure (some db's like postgresql require this)
        
    # create the table by automatically figuring out the field types
    cols = []
    tablecolumns = table.get_columns()
    for column in tablecolumns:
      typ = column.get_type()
      try:
        dbtype = picalo.TYPE_TO_DB[typ]
        cols.append(column.name + ' ' + dbtype)
      except (AttributeError, KeyError):  # a string type, so figure out how big
        if len(column) > 0:
          length = max(1, max([ len(str(val)) for val in column ]))
        else:
          length = 100
        if length <= 255:
          cols.append(column.name + ' varchar(' + str(length) + ')')
        else:
          cols.append(column.name + ' text')
    try:
      cursor = self.cursor()
      cursor.execute('CREATE TABLE ' + name + ' (' + ', '.join(cols) + ')')
    finally:
      self.commit()
      cursor.close()
    self.commit()
  

  def post_table(self, table, name, replace=False, add_if_empty=False):
    '''Creates a new table in the database and posts the records
       in the given table.  If a table with the given name
       already exists in the table, the method throws an error unless
       the "replace" option is True.  
       
       This is a convenience method provided to make importing of data from
       text files (CSV, TSV, etc.) and other sources into databases easy.
       The example shows how a CSV file can be posted to database in
       just two lines of code.  
       
       The method always tries to create a new table in
       the database -- it will not append records into an existing table.
       If the table cannot be created (if it exists, for example), an 
       error is thrown.  If the "replace" option is True, any
       existing tables by this name are dropped before the new table
       is created. 
       
       The method automatically commits the data to the database.  You cannot
       use rollback after this method has finished.  This is required by
       some databases after creation of a table, so it has to be done.
       
       Example:
        >>> myconn = Database.PostgreSQLConnection('mydb')
        >>> data = Table([('id', int), ('name', unicode)],[
        ...   [ 1, 'Benny' ],
        ...   [ 2, 'Vijay' ],
        ... ])
        >>> myconn.post_table(data, 'mytable', True)
        >>> myconn.table('SELECT * FROM mytable').view()         
        +----+-------+
        | id |  name |
        +----+-------+
        |  1 | Benny |
        |  2 | Vijay |
        +----+-------+
  
       @param table:        The picalo table to post
       @type  table:        Table
       @param name:         The new database table name
       @type  name:         str
       @param replace:      Whether to replace any existing database tables with the given name.  If the database table exists and replace is False (the default), the method will throw an error.
       @type  replace:      bool
       @param add_if_empty: Whether to add fields that are empty (None or '') or to simply leave them out of the query.
       @type  add_if_empty: bool
    '''
    # create the new table
    self._create_database_table(table, name, replace)
    
    # add the records
    try:
      tablecolumns = table.get_columns()
      for recindex in range(len(table)):
        show_progress('Uploading records...', float(recindex) / float(len(table)))
        rec = table[recindex]
        sql = self.insert_query_builder(name)
        for i in range(len(tablecolumns)):
          sql.add(tablecolumns[i].name, rec[i], add_if_empty=add_if_empty)
        sql.execute()
        self.commit()
    finally:
      self.commit()
      clear_progress()
      
      
  def copy_table(self, source_connection, source_tablename, dest_tablename, replace=False):
    '''Copies a table from a database into this connection.  This method pulls records one by one
       from the source connection and posts them to this connection.  It
       automatically creates the new destination table, optionally replacing any existing
       tables with the name.
       
       This is a convenience method provided to make importing of data from
       other databases easy.  This method is different from post_table because it
       is more memory-efficient.  The post_table method requires that you have an
       existing Picalo Table, which means all of the data needs to be in memory at
       once.  This method copies record by record, meaning it only needs to hold one
       record at a time.  This method works only with database connections, not with 
       CSV or other types of sources.
       
       The method always tries to create a new table in
       the database -- it will not append records into an existing table.
       If the table cannot be created (if it exists, for example), an 
       error is thrown.  If the "replace" option is True, any
       existing tables by this name are dropped before the new table
       is created. 
       
       The method automatically commits the data to the database.  You cannot
       use rollback after this method has finished.  This is required by
       some databases after creation of a table, so it has to be done.
    '''
    # check data types
    assert isinstance(source_connection, _Connection), 'The source_connection parameter must be a valid Picalo database connection'
    assert isinstance(source_tablename, types.StringTypes), 'The source table name parameter must be a string.'
    assert source_tablename != '', 'Please enter a table name for the source table name.'
    assert isinstance(dest_tablename, types.StringTypes), 'The destination tablename parameter must be a string.'
    assert source_tablename != '', 'Please enter a table name for the destination table name.'
    
    # query the data for this table
    source_cursor = source_connection.cursor()
    try:
      table = source_cursor.table("SELECT * FROM %s" % (source_tablename, ))
    
      # create the new table
      self._create_database_table(table, dest_tablename, replace)
    
      # add the records.  this method takes advantage of the fact that database-based tables
      # are loaded just in time.  since the code pulls the record data directly from the
      # cursor rather than the table variable, the data is never cached in the table object.
      try:
        for recindex in range(len(table)):
          show_progress('Copying records...', float(recindex) / float(len(table)))
          rec = table[recindex]
          sql = self.insert_query_builder(dest_tablename)
          for i in range(table.column_count()):
            sql.add(table.column(i).name, rec[i], add_if_empty=True)
          sql.execute()
          self.commit()
      finally:
        self.commit()
        clear_progress()
    finally:
      source_cursor.close()    


  def __str__(self):
    '''Returns a string representation of this connection'''
    return repr(self)


  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Connection decorator>: ' + repr(self._decorated_object)


  def save(self, filename):
    '''Saves the database connection'''
    # actual function def is below the classes in this file
    save(self, filename)
    
  
  #########   Specialized methods that subclasses should override   ##################

  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    pass
    
  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    return []
    
    
  def _get_columns(self, tablename):
    '''Returns a list of the columns in the given table.  Subclasses may have a more efficient way to do this.'''
    cursor = self.cursor()
    cursor.execute("SELECT * FROM " + tablename)
    colnames = [ row[0] for row in cursor.description ]
    cursor.close()
    return colnames


        
    
    
#########################################################################
###   Specialization classes for specific databases


class _SqliteConnection(_Connection):
  '''A specialization class for sqlite3 connections'''
  
  QUERY_PARAMETER = '?'  
  
  def __init__(self, dbconnection, func, args):
    _Connection.__init__(self, dbconnection, func, args)
    self._tablenames = None

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._SqliteConnection decorator>: ' + repr(self._decorated_object)

  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    # how to do this?  Sqlite doesn't give me the column types in the cursor description list!
    pass
    

  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    if refresh or self._tablenames == None:
      self._tablenames = []
      try:
        cursor = self.cursor()
        self._tablenames = [ row[0] for row in cursor.query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name") ]
        cursor.close()
      except:  # thrown when connection is closed
        pass
    return self._tablenames


class _Psycopg2Connection(_Connection):
  '''A specialization class for psycopg2 connections'''
  def __init__(self, dbconnection, func, args):
    _Connection.__init__(self, dbconnection, func, args)
    self._tablenames = None
  
  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Psycopg2Connection decorator>: ' + repr(self._decorated_object)

  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    for i in range(len(cursor.description)):
      typecode = cursor.description[i][1]
      if typecode in ( 1114, 1184, 704, 1186, ): # date time types
        table.set_type(i, DateTime)
      elif typecode in ( 21, 23, ): # integer
        table.set_type(i, int)
      elif typecode in ( 20, ):  # long integer
        table.set_type(i, long)
      elif typecode in ( 701, 700, 1700, ): # float
        table.set_type(i, number)
        table.set_format(i, '"%0.4f" % value')


  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    if refresh or self._tablenames == None:
      self._tablenames = []
      try:
        cursor = self.cursor()
        self._tablenames = [ row[0] for row in cursor.query("select tablename from pg_tables where schemaname='public'") ]
        cursor.close()
      except:  # thrown when connection is closed
        pass
    return self._tablenames
    

  def _get_columns(self, tablename):
    '''Returns a list of the columns in the given table'''
    cursor = self.cursor()
    columns = [ row[0] for row in cursor.query("select column_name from information_schema.columns where table_name='%s'" % (tablename, )) ]
    cursor.close()
    return columns
    


    
class _PyGreSQLConnection(_Connection):
  '''A spoecialization class for PyGreSQL connections'''    
  def __init__(self, dbconnection, func, args):
    _Connection.__init__(self, dbconnection, func, args)
    self._tablenames = None

  
  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._PyGreSQLConnection decorator>: ' + repr(self._decorated_object)


  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    for i in range(len(cursor.description)):
      typecode = cursor.description[i][1]
      if typecode in ( 'abstime', 'reltime', 'tinterval', 'date', 'time', 'timespan', 'timestamp', 'timestamptz', 'interval', ): # date time types
        table.set_type(i, DateTime)
      elif typecode in ( 'int2', 'int4', 'serial', ): # integer
        table.set_type(i, int)
      elif typecode in ( 'int8', ):  # long integer
        table.set_type(i, long)
      elif typecode in ( 'float4', 'float8', 'numeric', 'money' ): # float
        table.set_type(i, number)
        table.set_format(i, '"%0.4f" % value')
      elif typecode in ( 'bool', ): # boolean
        table.set_type(i, boolean)


  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    if refresh or self._tablenames == None:
      self._tablenames = []
      try:
        cursor = self.cursor()
        self._tablenames = [ row[0] for row in cursor.query("select tablename from pg_tables where schemaname='public'") ]
        cursor.close()
      except:  # thrown when connection is closed
        pass
    return self._tablenames
    

  def _get_columns(self, tablename):
    '''Returns a list of the columns in the given table'''
    cursor = self.cursor()
    columns = [ row[0] for row in cursor.query("select column_name from information_schema.columns where table_name='%s'" % (tablename, )) ]
    cursor.close()
    return columns
    

    

class _OdbcConnection(_Connection):
  '''A specialization class for PyODBC connections'''
  
  QUERY_PARAMETER = '?'  # PyODBC has a special one (should be %s per spec)
  
  def __init__(self, dbconnection, func, args):
    _Connection.__init__(self, dbconnection, func, args)
    self._tablenames = None

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._OdbcConnection decorator>: ' + repr(self._decorated_object)

  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    for i in range(len(cursor.description)):
      typecode = cursor.description[i][1]
      size = cursor.description[i][3]
      precision = cursor.description[i][4]
      if typecode == datetime.datetime:
        table.set_type(i, DateTime)
      elif typecode == types.IntType:
        table.set_type(i, int)
      elif typecode == types.FloatType:
        table.set_type(i, number)
        table.set_format(i, '"%0.4f" % value')

  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    if refresh or self._tablenames == None:
      self._tablenames = []
      try:
        cursor = self.cursor()
        self._tablenames = [ row[2] for row in cursor.tables() if row[3] == 'TABLE' ]
        cursor.close()
      except:  # thrown when connection is closed
        pass
    return self._tablenames


  def _get_columns(self, tablename):
    '''Returns a list of the columns in the given table'''
    cursor = self.cursor()
    colnames = [ row[3] for row in cursor.columns(table=tablename) ]
    cursor.close()
    return colnames
    

class _MySQLdbConnection(_Connection):
  '''A specialization class for MySQLdb connections'''
  def __init__(self, dbconnection, func, args):
    _Connection.__init__(self, dbconnection, func, args)
    self._tablenames = None

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._MySQLdbConnection decorator>: ' + repr(self._decorated_object)

  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    for i in range(len(cursor.description)):
      typecode = cursor.description[i][1]
      if typecode in ( 12, 10, 13, 14, ): # date time types
        table.set_type(i, DateTime)
      elif typecode in ( 1, 2, 3, ): # integer
        table.set_type(i, int)
      elif typecode in ( 8, 9, ):  # long integer
        table.set_type(i, long)
      elif typecode in ( 4, 5, 0, ): # float
        table.set_type(i, number)
        table.set_format(i, '"%0.4f" % value')


  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    if refresh or self._tablenames == None:
      self._tablenames = []
      try:
        cursor = self.cursor()
        self._tablenames = [ row[0] for row in cursor.query("show tables") ]
        cursor.close()
      except:  # thrown when connection is closed
        pass
    return self._tablenames


class _OracleConnection(_Connection):
  '''A specialization class for cx_Oracle connections'''
  def __init__(self, dbconnection, func, args):
    _Connection.__init__(self, dbconnection, func, args)
    self._tablenames = None

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._OracleConnection decorator>: ' + repr(self._decorated_object)

  def _set_table_types(self, cursor, table):
    '''Helper method for _Connection.table().  After the query is run, this method
       uses the cursor to set the column types appropriately.'''
    import cx_Oracle
    for i in range(len(cursor.description)):
      typecode = cursor.description[i][1]
      if typecode in ( cx_Oracle.DATETIME, cx_Oracle.TIMESTAMP ): # date time types
        table.set_type(i, DateTime)
      elif typecode in ( cx_Oracle.NUMBER, ): # integer
        if cursor.description[i][5] == 0:  # scale?
          table.set_type(i, long)
        else:
          table.set_type(i, number)
          table.set_format(i, '"%0.4f" % value')

  def list_tables(self, refresh=True):
    '''Returns the table names in this database as a list'''
    if refresh or self._tablenames == None:
      self._tablenames = []
      try:
        cursor = self.cursor()
        self._tablenames = [ row[0] for row in cursor.query("SELECT table_name FROM user_tables ORDER BY table_name") ]
        cursor.close()
      except:  # thrown when connection is closed
        pass
    return self._tablenames  
    
    
    

##############################################################
###   Our cursor decorator.  It is created automatically
###   by _Connection.cursor() and other methods in
###   _Connection.


class _Cursor(picalo.AbstractDecorator):
  '''A database cursor.  Since Picalo automatically manages cursors,
     you don't need to create these directly.
  '''
  def __init__(self, parent, obj):
    picalo.AbstractDecorator.__init__(self, obj)
    self.parent = parent
    self.columns_map = {}
  
  def execute(self, sql, parameters=None):
    '''Executes the given sql'''
    assert isinstance(sql, types.StringTypes), 'Invalid SQL string: ' + str(sql)
    if parameters == None:
      self._decorated_object.execute(sql)
    else:
      self._decorated_object.execute(sql, parameters)
    if self.description == None:
      self.columns_map = {}
    else:
      self.columns_map = dict([ (self.description[i][0], i) for i in range(len(self.description)) ])
  

  def query(self, sql, parameters=None):
    '''Runs an SQL query.  The results of this method can be iterated directly.  Although you cannot
       randomly access the records by index (only sequentially in a for loop), this method is 
       much more efficient than table() because it pulls only one record into memory at a time.'''
    # types are checked in execute
    try:
      show_progress('Running query...', 0.0)
      self.execute(sql, parameters)
      return self
    finally:
      clear_progress()
    

  def query1(self, sql, parameters=None):
    '''Runs an SQL query (using cursor.execute) and returns the first record
       in the result set.  This is useful when you only expect one row (such as
       SELECT MAX(...) queries).
    '''
    # types are checked in execute
    try:
      show_progress('Running query...', 0.0)
      self.query(sql, parameters)
      return self.fetchone()
    finally:
      clear_progress()
    

  def table(self, sql, parameters=None):
    '''See Database.Connection.table() for information on this method.'''
    query = Query(sql, parameters)
    query.execute(self)
    return query.table
        
    
  def __iter__(self):
    '''Returns an iterator to the most recent results'''
    while True:
      rec = self.fetchone()
      if rec == None:
        return
      yield rec    
    

  def __str__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Cursor decorator>: ' + str(self._decorated_object)
    

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Cursor decorator>: ' + repr(self._decorated_object)



########################################################
###  Query extension to Table to differentiate the two
    
#class Query(Table):
#  '''Extension to table to load a query'''
#  def __init__(self,     
    
    

################################################
###   Classes to help in creating SQL queries


class QueryBuilderException(Exception):
  '''Simple exception to report query builder problems, with an embedded error.'''
  def __init__(self, e, msg):
    self.e = e
    self.msg = msg
    
  def __repr__(self):
    return 'Error in query: %s; %s' % (self.msg, repr(self.e))
    
  def __str__(self):
    return repr(self)
    

class _BaseQueryBuilder:
  '''The base of query builder with common code.'''
  def __init__(self, tablename, connection):
    self._tablename = tablename
    self._db = connection
    self._fieldnames = []
    self._values = []
    self._wherenames = []
    self._wherevalues = []

  
  def add(self, field, value, add_if_empty=True):
    """
    Adds a field/value pair to the statement,
    optionally skipping the add if the value is None or empty ('').
    This method is only valid for update-type queries and is ignored
    in select queries.
    """
    if not add_if_empty and (value == '' or field == '' or value == None or field == None):
      return
    if field in self._fieldnames:
      index = self._fieldnames.index(field)
      self._values[index] = value
    else:
      self._fieldnames.append(field)
      self._values.append(value)
      
      
  def add_where(self, field, value, add_if_empty=True):
    '''Adds a field/value pair to the statement for the WHERE
       clause.  This method is only used in statements where this
       makes sense (select, update).  It is ignored in insert queries.
    '''
    if not add_if_empty and (value == '' or field == '' or value == None or field == None):
      return
    if field in self._wherenames:
      index = self._wherenames.index(field)
      self._wherevalues[index] = value
    else:
      self._wherenames.append(field)
      self._wherevalues.append(value)
          
      
  def __setitem__(self, field, value):
    '''Allows dictionary-use of the object to call the add method.
       It always adds the value, even if it is None or empty.
    '''
    self.add(field, value)
    
    
  def __getitem__(self, field):
    '''Returns the item with the given field name'''
    return self.get(field)
    
    
  def get(self, field, default=None):
    '''Returns the item with the given field name, or the default value if none exists'''
    if field in self._fieldnames:
      index = self._fieldnames.index(field)
      return self._values[index]
    return default
    

  def execute(self):
    '''Executes the SQL statement.  This method should be called for 
       insert and update queries.
       Does *not* commit if transactions are being used.
    '''
    cursor = self._db.cursor()
    try:
      cursor.execute(self.get_query_string(), self.get_parameters())
    except Exception, e:
      raise QueryBuilderException(e, str(self))
    cursor.close()


  def get_query_string(self):
    '''Returns the query string as it will be sent to the database.'''
    raise NotImplementedError, 'Subclass of _BaseQueryBuilder did not implement required method get_query_string'


  def get_parameters(self):
    '''Returns the parameters as they will be sent to the database'''
    raise NotImplementedError, 'Subclass of _BaseQueryBuilder did not implement required method get_parameters'


  def __len__(self):
    '''Returns the number of fields in this query'''
    return len(self._fieldnames)
    
    
  def _format(self, st):
    '''Helper method to ensure that special characters are escaped correctly'''
    return str(st).replace('"', '\\"')    
    
    
  def __str__(self):
    return '<cursor>.execute("' + self.get_query_string() + '", ' + str(self.get_parameters()) + ")"



class UpdateQueryBuilder(_BaseQueryBuilder):
  """Helps in building a simple update SQL call.  This class is useful
     when creating SQL from a script, piece by piece.  See 
     _Connection.update_query_builder() for more information."""
  def __init__(self, tablename, connection):
    _BaseQueryBuilder.__init__(self, tablename, connection)
    

  def get_query_string(self):
    '''Returns the query string as it will be sent to the database.'''
    sql = []
    sql.append("UPDATE " + self._format(self._tablename))
    if len(self._fieldnames) > 0:
      params = [ self._format(name) + "=" + self._db.QUERY_PARAMETER for name in self._fieldnames ]
      sql.append(" SET " + ', '.join(params))
    if len(self._wherenames) > 0:
      where = [ self._format(name) + "=" + self._db.QUERY_PARAMETER for name in self._wherenames ]
      sql.append(" WHERE " + ', '.join(where))
    return ''.join(sql)
    
  
  def get_parameters(self):  
    '''Returns the parameters as they will be sent to the database'''
    params = []
    for val in self._values + self._wherevalues:
      if isinstance(val, Date):
        params.append(val.strftime('%Y-%m-%d'))
      elif isinstance(val, DateTime):
        params.append(val.strftime('%Y-%m-%d %H:%M:%S'))
      else:
        params.append(val)
    return params
    

class InsertQueryBuilder(_BaseQueryBuilder):
  """Helps in building a simple insert SQL call.  This class is useful
     when creating SQL from a script, piece by piece.  See 
     _Connection.insert_query_builder() for more information."""
  def __init__(self, tablename, connection):
    _BaseQueryBuilder.__init__(self, tablename, connection)
    

  def get_query_string(self):
    '''Returns the query string as it will be sent to the database.'''
    sql = []
    sql.append("INSERT INTO " + self._format(self._tablename))
    if len(self._fieldnames) > 0:
      sql.append(' (')
      sql.append(', '.join([ self._format(name) for name in self._fieldnames ]))
      sql.append(') VALUES (')
      sql.append(', '.join([self._db.QUERY_PARAMETER for val in self._values]))
      sql.append(')')
    return ''.join(sql)
    
  
  def get_parameters(self):  
    '''Returns the parameters as they will be sent to the database'''
    params = []
    for val in self._values:
      if isinstance(val, Date):
        params.append(val.strftime('%Y-%m-%d'))
      elif isinstance(val, DateTime):
        params.append(val.strftime('%Y-%m-%d %H:%M:%S'))
      else:
        params.append(val)
    return params
    


class SelectQueryBuilder(_BaseQueryBuilder):
  """Helps in building a simple select SQL call.  This class is useful
     when creating SQL from a script, piece by piece. See 
     _Connection.select_query_builder() for more information."""
  def __init__(self, tablename, select_fields, connection):
    _BaseQueryBuilder.__init__(self, tablename, connection)
    assert isinstance(select_fields, (types.TupleType, types.ListType)), 'The select_fields parameter must be a list or tuple of field names (or *) to select from the table.'
    assert len(select_fields) > 0, 'The select_fields parameter must be a list or tuple of field names (or *) to select from the table.  You must provide at least one field name.'
    self.select_fields = select_fields
    

  def get_query_string(self):
    '''Returns the query string as it will be sent to the database.'''
    sql = []
    sql.append("SELECT ")
    sql.append(', '.join([ self._format(name) for name in self.select_fields ]))
    sql.append(" FROM " + self._format(self._tablename))
    if len(self._wherenames) > 0:
      where = [ self._format(name) + "=" + self._db.QUERY_PARAMETER for name in self._wherenames ]
      sql.append(" WHERE " + ', '.join(where))
    return ''.join(sql)
    

  def get_parameters(self):  
    '''Returns the parameters as they will be sent to the database'''
    params = []
    for val in self._wherevalues:
      if isinstance(val, Date):
        params.append(val.strftime('%Y-%m-%d'))
      elif isinstance(val, DateTime):
        params.append(val.strftime('%Y-%m-%d %H:%M:%S'))
      else:
        params.append(val)
    return params
    

  def query(self):
    '''Runs the query and returns a cursor to the results data set'''
    cursor = self._db.cursor()
    return cursor.query(self.get_query_string(), self.get_parameters())

    
  def query1(self):
    '''Runs the query and returns a single record (i.e. tuple) of the first result.
       This is useful when you are sure you will get only one result back from
       the query (such as a COUNT operator).'''
    cursor = self._db.cursor()
    return cursor.query1(self.get_query_string(), self.get_parameters())
    
    
  def table(self):
    '''Runs the query and returns a Picalo table containing the results
       of the query.'''
    cursor = self._db.cursor()
    return cursor.table(self.get_query_string(), self.get_parameters())
    


############################################
###   Load and save routines

# pickle protocol to use
PICKLE_PROTOCOL = 2


def load(filename):
  '''Loads the connection from the given filename.
  
     @param filename: The filename to load from.  This can also be an open stream.
     @type  filename: str
  '''
  fileopened = False
  if type(filename) in types.StringTypes:
    filepath = filename
    filename = open(filename, 'rb')
    fileopened = True
    
  # ungzip it on the fly (if it is not already a GzipFile)
  startedzip = False
  gin = filename
  if not isinstance(gin, gzip.GzipFile):
    gin = gzip.GzipFile(fileobj=gin, mode='rb')
    startedzip = True
      
  # read the data and create the connection
  data = pickle.load(gin)
  func = globals()[data['connect_func']]
  conn = func(**data['connect_args'])
  conn.modified = False
  
  # close up shop and return
  if startedzip:
    gin.close() 
  if fileopened:
    conn.filename = filepath
    filename.close()
  return conn
  
  
def save(conn, filename):
  '''Saves the given connection to the filename.
  
     @param conn:     The database connection to save.
     @type  conn:     Picalo Database Connection
     @param filename: The filename to save to.  This can also be an open stream.
     @type  filename: str
  '''
  assert isinstance(conn, _Connection), 'Only database connections opened with Picalo can be saved with this method.'
  
  # get a file pointer
  fileopened = False
  if type(filename) in types.StringTypes:
    conn.filename = filename
    filename = open(filename, 'wb')
    fileopened = True
  
  # gzip it on the fly (if it is not already a GzipFile)
  openedzip = False
  gout = filename
  if not isinstance(gout, gzip.GzipFile):
    gout = gzip.GzipFile(fileobj=gout, mode='wb')
    openedzip = True
    
  # save the database connection information
  data = {
    'connect_func': conn._connect_func,
    'connect_args': conn._connect_args,
  }
  pickle.dump(data, gout, PICKLE_PROTOCOL)
  
  # close up shop
  gout.flush()
  if openedzip:
    gout.close()
  if fileopened:
    filename.close()
  conn.modified = False
  
  
  
  
################################################
###   Query object

class Query:
  '''Represents a query on a database.'''
  def __init__(self, sql, parameters=None, conn=None):
    '''Creates a new query object.
    
       @param sql:           The SQL string to execute.
       @type  sql:           string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @param conn:          If not None, the query is immediately executed with the given connection.  This parameter can also be a Picalo _Cursor object.
       @type  conn:          Database._Connection or Database._Cursor object
    '''
    assert sql, 'The sql parameter cannot be empty.'
    assert isinstance(sql, types.StringTypes), 'The sql parameter must be an SQL string.'
    self._connect_func = None
    self._connect_args = None
    self.filename = None
    self.table = None
    self.set_sql(sql, parameters, conn)  # adds more class variables, see this method


  def set_sql(self, sql, parameters=None, conn=None):
    '''Modifies the sql of this connection, potentially re-executing it with the given connection'''
    self._modified = True
    self._sql = sql
    self._parameters = parameters
    if conn != None:
      self.execute(conn)
    
    
  def get_sql(self):
    '''Returns the SQL for this query'''
    return self._sql


  def execute(self, conn):
    '''Run the query using the given database connection.
    
       @param conn:          The connection to execute the query on.  This parameter can also be a Picalo _Cursor object.
       @type  conn:          Database._Connection or Database._Cursor object
    '''
    # check the parameter
    assert isinstance(conn, (_Connection, _Cursor)), 'The conn parameter must be a Picalo connection (or cursor) object'
    if isinstance(conn, _Connection):
      cursor = conn.cursor()
    else:
      cursor = conn
    
    # save the database connection information.  This helps the Picalo GUI
    # match queries to database connections when queries are run.
    if self._connect_func != cursor.parent._connect_func:
      self.modified = True
      self._connect_func = cursor.parent._connect_func
    if self._connect_args != cursor.parent._connect_args:
      self.modified = True
      self._connect_args = cursor.parent._connect_args
    
    # run the query
    cursor.query(self._sql, self._parameters)
    assert cursor.description != None, 'You must first run a query that returns results to create a Table object!'
    
    # if the table currently exists, notify that it will be changing
    if self.table != None:
      self.table._notify_listeners(level=3)
    
    # first create the table
    self.table = Table(picalo.make_unique_colnames(picalo.ensure_valid_variables([ desc[0] for desc in cursor.description ])))
    
    # set the types
    cursor.parent._set_table_types(cursor, self.table)
    
    # set up the table data
    for row in cursor:
      self.table.append(row)
    
  
  def is_changed(self):
    '''Returns whether the table has been changed since loading'''
    return self._modified
    
    
  def save(self, filename):
    '''Saves the query to the given filename'''
    save_query(self, filename)
    
    
  def view(self):
    '''Opens a spreadsheet-view of the table if Picalo is being run in GUI mode.
       If Picalo is being run in console mode, it redirects to prettyprint().
       This is the preferred way of viewing the data in a table.
    '''
    # this is explicitly included in the class so it runs even if the table
    # hasn't been loaded.  the GUI will execute automatically.
    picalo.TableModule.view(self)
    

  def __eq__(self, other):
    '''Returns whether this query is equal to another query (or list of lists).'''
    if isinstance(other, (Query)):
      for name in [ '_sql', '_parameters', '_connect_func', '_connect_args' ]:
        if getattr(self, name) != getattr(other, name):
          return False
      return True
    return False
    
    
    
  ################################################
  ###   Pass-through most methods to Table    
    
  def __getattr__(self, name):
    # class methods are already searched before __getattr__ gets called (not true with __setattr__, btw)
    assert self.table != None, 'You must first execute the query before calling "%s"' % (name, )
    return getattr(self.table, name)
    
    
##########################################
###   Load and save methods for query
def load_query(filename):
  '''Loads the query from the given filename.
  
     @param filename: The filename to load from.  This can also be an open stream.
     @type  filename: str
  '''
  fileopened = False
  if type(filename) in types.StringTypes:
    filepath = filename
    filename = open(filename, 'rb')
    fileopened = True
    
  # ungzip it on the fly (if it is not already a GzipFile)
  startedzip = False
  gin = filename
  if not isinstance(gin, gzip.GzipFile):
    gin = gzip.GzipFile(fileobj=gin, mode='rb')
    startedzip = True
      
  # read the data and create the connection
  data = pickle.load(gin)
  query = Query(data['sql'], data['parameters'])
  query._connect_func = data['connect_func']
  query._connect_args = data['connect_args']
  query._modified = False
  
  # close up shop and return
  if startedzip:
    gin.close() 
  if fileopened:
    query.filename = filepath
    filename.close()
  return query
  
  
def save_query(query, filename):
  '''Saves the given connection to the filename.
  
     @param query:    The query object to save.
     @type  query:    Picalo Query object
     @param filename: The filename to save to.  This can also be an open stream.
     @type  filename: str
  '''
  assert isinstance(query, Query), 'Only Picalo Query objects can be saved with this method.'
  
  # get a file pointer
  fileopened = False
  if type(filename) in types.StringTypes:
    query.filename = filename
    filename = open(filename, 'wb')
    fileopened = True
  
  # gzip it on the fly (if it is not already a GzipFile)
  openedzip = False
  gout = filename
  if not isinstance(gout, gzip.GzipFile):
    gout = gzip.GzipFile(fileobj=gout, mode='wb')
    openedzip = True
    
  # save the database connection information
  data = {
    'sql': query._sql,
    'parameters': query._parameters,
    'connect_func': query._connect_func,
    'connect_args': query._connect_args,
  }
  pickle.dump(data, gout, PICKLE_PROTOCOL)
  
  # close up shop
  gout.flush()
  if openedzip:
    gout.close()
  if fileopened:
    filename.close()
  query._modified = False
  