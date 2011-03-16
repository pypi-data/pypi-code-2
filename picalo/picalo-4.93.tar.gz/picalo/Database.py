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
# Picalo is distributed in the hope that it will been useful,                        #
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
import ZODB.DB
import persistent
from persistent.dict import PersistentDict


__doc__ = '''
  This module provides easy access to DB-API 2.0 tables.  It is a decorator
  for connections and cursors.  Cursor results can be accessed efficiently
  via field name or index.  
  
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
     applications where you want to use SQL but don't need a "real" database server
     like MySQL, PostgreSQL, or Oracle.  Since it comes with Picalo, it's
     ready to go immediately -- nothing is required except a Picalo install.
     
     @param    dirname:  The directory to store database files in, or ":memory:" to keep everything in memory.
     @type     dirname:  str
     @returns: A database connection.
     @rtype:   Connection
  '''
  assert isinstance(dirname, types.StringTypes), 'Invalid directory name: ' + str(dirname)
  func_args = {
    'dirname': dirname,
  }
  db = _SqliteConnection(func_args)
  db.open()
  return db


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
     @rtype:   Connection
  '''
  assert isinstance(dsn_name, types.StringTypes), 'Invalid DSN name: ' + str(dsn_name)
  assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
  assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
  func_args = {
    'dsn_name': dsn_name,
    'username': username,
    'password': password,
  }
  db = _OdbcConnection(func_args)
  db.open()
  return db


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
     @rtype:   Connection
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
  db = _Psycopg2Connection(func_args)
  db.open()
  return db


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
     @rtype:   Connection
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
  db = _PyGreSQLConnection(func_args)
  db.open()
  return db


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
     @rtype:   Connection
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
  db = _MySQLdbConnection(func_args)
  db.open()
  return db


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
     @rtype:   Connection
  '''
  assert isinstance(dsn, types.StringTypes), 'Invalid DSN: ' + str(dsn)
  assert isinstance(username, (types.StringTypes, types.NoneType)), 'Invalid username: ' + str(username)
  assert isinstance(password, (types.StringTypes, types.NoneType)), 'Invalid password: ' + str(password)
  func_args = {
    'dsn': dsn,
    'username': username,
    'password': password,
  }
  db = _OracleConnection(func_args)
  db.open()
  return db



################################################################################
###   Private methods and classes in the module:                             ###
################################################################################


class Connection(persistent.Persistent):
  '''The base class of connections.  This class abstract; a subclass is always created.'''
  
  QUERY_PARAMETER = '%s'    # the string used for parameters in queries
  TRANSIENT_VARIABLE_NAMES = [ 'dbconnection', '_table_cache' ]
  
  def __init__(self, connect_args):
    assert type(self) != Connection, 'Connection is an abstract class and cannot be instantiated directly.  Instead, create a subclass like MySQLConnection, PostgreSQLConnection, SqliteConnection, etc.'
    self._table_cache = {}   # cache to hold tables automatically loaded from the database
    self._connect_args = connect_args
    self.dbconnection = None
    self.modified = True
    self.queries = PersistentDict()
    
    
  def __getstate__(self):
    '''Returns the state of the object for ZODB serialization.  First removes transient variables'''
    c = persistent.Persistent.__getstate__(self)
    for varname in self.TRANSIENT_VARIABLE_NAMES: # remove any variables that are transient
      del c[varname]
    return c
        
      
  def __getattr__(self, key):
    '''Returns the given attribute of the class.  
    
       This method allows dot (.) notation access to both queries and tables
       in the database.  It first searches the names of queries saved in this connection,
       then it searches table names in the database.
       
       For example, conn.mytable will first search for a query named "mytable".  If it 
       finds the query, it runs the query and returns the Query object with data ready
       for access.  If no query named "mytable" is found, it automatically runs
       "SELECT * FROM mytable" and pulls the records into a table for you.
    '''
    # first look for a query
    if self.queries.has_key(key):
      return self.queries[key]
      
    # next try our table cache
    if self._table_cache.has_key(key):
      return self._table_cache[key]
      
    # now try to load from the database
    if not self.is_open():
      self.open()
    useProgress = picalo.useProgress
    picalo.useProgress = False
    try:
      if key in self.list_tables():
        table = self.table("SELECT * FROM " + key) # load the table and store in the cache
        self._table_cache[key] = table
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
      self._table_cache = {}
    else:                    # refresh a single table
      if self._table_cache.has_key(tablename):
        del self._table_cache[tablename]
          
          
  def open(self):
    '''Opens the connection to the database using the connect parameters the object
       was created with.  If you want to change the connection parameters, create a 
       new Database.*Connection object.
    '''
    self.dbconnection = self._open_connection() # subclasses define this method
    assert self.dbconnection != None, 'The subclass did not correctly open the database connection'
    
  
  def is_open(self):
    '''Returns whether this connection is opened to the database'''
    return self.dbconnection != None


  def close(self):
    '''Closes the connection'''
    self.dbconnection.close()       
    self.dbconnection = None   
          
  
  def cursor(self):
    '''Returns a cursor to the database.  Since Picalo manages cursors automatically,
       most users don't need to access them directly.   The method is provided for
       advanced users who want to explicitly manage cursors.
       
       Cursors allow direct access to the underlying database driver's methods.
       For example, cursor.execute() and cursor.fetchmany() can be used to efficiently
       iterate through a SELECT query.
       
       @return:    A cursor to the database.
       @rtype:     Database._Cursor
    '''
    if not self.is_open():
      self.open()
    return _Cursor(self, self.dbconnection.cursor())
    
    
  def table(self, sql, parameters=None):
    '''This method creates a temporary table from the results of a query.
       Users should normally use the create_query() method instead of this one
       because it saves the query in the connection object for later use.  
       However, if you have no need for the query later, call this method
       and get a table created directly from the results.  The table is
       static in that it does not update as changes are made to the database.
        
       @param sql:   The SQL string to execute.
       @type  sql:   string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @return:      A picalo table containing the results.
       @rtype:       Table
    '''
    # create a query object, but don't add it to our list
    return Query(self, sql, parameters, execute=True)
    

  def create_query(self, name, sql, parameters=None, execute=True):
    '''Creates a new Picalo Query and attaches it to this database
       connection.  The query is executed immediately by default, and
       the Query object can be accessed just like a regular Picalo table,
       including any method of the Table object.
       
       Query objects can be accessed directly via the dot (.) notation,
       so they should have unique names from tables in the database.
       
       If you just want to run a quick query without adding it to the 
       connection, use conn.cursor().query() or conn.cursor.execute().
       However, this method is normally the preferred way to do queries.
       
       @param name:        The name of the query this connection will refer to it by
       @type  name:        str
       @param sql:         The SQL string to execute.
       @type  sql:         string
       @param parameters:  The parameters to be sent to the database.
       @type  parameters:  List or Tuple
       @param execute:     Whether this query should be executed automatically, making the results available immediately.
       @type  parameters:  boolean
       @return:            A Query object that acts exactly like a Table.
       @rtype:             Query
    '''
    assert isinstance(name, types.StringTypes), 'The name parameter must be a string.'
    assert name, 'The name parameter cannot be empty.'
    assert not self.queries.has_key(name), 'A query with the name %s already exists in this connection.  Please delete it before adding another with the same name.' % name
    query = Query(self, sql, parameters, execute)
    self.queries[name] = query
    return query
    
    
  def list_queries(self):
    '''Lists the names of the queries in this connection'''
    return self.queries.keys()
    
    
  def get_query(self, name, execute=True):
    '''Returns the query with the given name.  If the execute parameter is True, 
       the query is (re)run to make the data available (or refresh the results).
       
       Alternatively, you can use dot (.) notation to retrieve a query, as in
       conn.myquery.  This method of access always executes the query if needed.
    '''
    assert isinstance(name, types.StringTypes), 'The name parameter must be a string.'
    assert name, 'The name parameter cannot be empty.'
    assert self.queries.has_key(name), 'A query with the name %s does not exist in this connection' % name
    query = self.queries[name]
    if execute:
      query.execute()
    return query
    
    
  def delete_query(self, name):
    '''Removes a query from the database connection'''
    assert isinstance(name, types.StringTypes), 'The name parameter must be a string.'
    assert name, 'The name parameter cannot be empty.'
    assert self.queries.has_key(name), 'A query with the name %s does not exist in this connection' % name
    del self.queries[name]
    
  
  def commit(self):
    '''Commits any changes to the database.  If you make modifications of any
       kind to your database tables (INSERT, UPDATE, CREATE, etc.), you *must*
       commit those changes by calling commit().
       
       If you close a database connection without committing, you'll lose all
       changes.
       
       Analyses that only run SELECT calls on a database do not need to commit().
       
       See the execute() method for an example of committing.
    '''
    if not self.is_open():
      self.open()
    self.dbconnection.commit()
    
    
  def rollback(self):
    '''Rolls back any changes to the database since the last commit.'''
    if not self.is_open():
      self.open()
    self.dbconnection.rollback()
    

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
    assert isinstance(source_connection, Connection), 'The source_connection parameter must be a valid Picalo database connection'
    assert isinstance(source_tablename, types.StringTypes), 'The source table name parameter must be a string.'
    assert source_tablename != '', 'Please enter a table name for the source table name.'
    assert isinstance(dest_tablename, types.StringTypes), 'The destination tablename parameter must be a string.'
    assert source_tablename != '', 'Please enter a table name for the destination table name.'
    
    # query the data for this table
    table = source_connection.table("SELECT * FROM %s" % (source_tablename, ))
  
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


  def __str__(self):
    '''Returns a string representation of this connection'''
    return repr(self)


  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database.Connection decorator>: ' + repr(self.dbconnection)


  #########   Specialized methods that subclasses should override   ##################

  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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


class _SqliteConnection(Connection):
  '''A specialization class for sqlite3 connections'''
  
  QUERY_PARAMETER = '?'  
  
  def __init__(self, args):
    Connection.__init__(self, args)
    self._tablenames = None
    
  def _open_connection(self):
    import sqlite3
    return sqlite3.connect(self._connect_args['dirname'])
    

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._SqliteConnection decorator>: ' + repr(self.dbconnection)

  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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


class _Psycopg2Connection(Connection):
  '''A specialization class for psycopg2 connections'''
  def __init__(self, args):
    Connection.__init__(self, args)
    self._tablenames = None
  
  def _open_connection(self):
    '''Opens a connection to the database'''
    args = []
    args.append('dbname=%s' % (self._connect_args['database'], ))
    if username != None: args.append('user=%s' % (self._connect_args['username'], ))
    if password != None: args.append('password=%s' % (self._connect_args['password'], ))
    if host != None: args.append('host=%s' % (self._connect_args['host'], ))
    if port != None: args.append('port=%s' % (self._connect_args['port'], ))
    dsn = ' '.join(args)
    import psycopg2
    return psycopg2.connect(dsn)

  
  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Psycopg2Connection decorator>: ' + repr(self.dbconnection)

  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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
    


    
class _PyGreSQLConnection(Connection):
  '''A spoecialization class for PyGreSQL connections'''    
  def __init__(self, args):
    Connection.__init__(self, args)
    self._tablenames = None


  def _open_connection(self):
    '''Helper method that opens a connection to the database'''
    args = {}
    args['database'] = self._connect_args['database']
    if username != None: args['user'] = self._connect_args['username']
    if password != None: args['password'] = self._connect_args['password']
    if self._connect_args['host'] != None: 
      args['host'] = self._connect_args['host']
    else:
      args['host'] = 'localhost'
    if self._connect_args['port'] != None: args['host'] += ':' + str(self._connect_args['port'])
    import pgdb
    return pgdb.connect(**args)

  
  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._PyGreSQLConnection decorator>: ' + repr(self.dbconnection)


  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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
    

    

class _OdbcConnection(Connection):
  '''A specialization class for PyODBC connections'''
  QUERY_PARAMETER = '?'  # PyODBC has a special one (should be %s per spec)
  
  def __init__(self, args):
    Connection.__init__(self, args)
    self._tablenames = None
    
  def _open_connection(self):
    '''Helper method that opens a connection to the database'''
    dsn = 'DSN=%s' % (self._connect_args['dsn_name'], )
    if self._connect_args['username'] != None and self._connect_args['password'] != None:
      dsn = 'DSN=%s;UID=%s;PWD=%s' % (self._connect_args['dsn_name'], self._connect_args['username'], self._connect_args['password'])
    elif self._connect_args['password'] != None:
      dsn = 'DSN=%s;PWD=%s' % (self._connect_args['dsn_name'], self._connect_args['password'])
    import pyodbc
    db = pyodbc.connect(dsn)

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._OdbcConnection decorator>: ' + repr(self.dbconnection)

  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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
    

class _MySQLdbConnection(Connection):
  '''A specialization class for MySQLdb connections'''
  def __init__(self, args):
    Connection.__init__(self, args)
    self._tablenames = None

  def _open_connection(self):
    '''Helper method that opens a connection to the database'''
    args = {}
    args['db'] = self._connect_args['database']
    if self._connect_args['username'] != None: args['user'] = self._connect_args['username']
    if self._connect_args['password'] != None: args['passwd'] = self._connect_args['password']
    if self._connect_args['host'] != None: args['host'] = self._connect_args['host']
    if self._connect_args['port'] != None: args['port'] = self._connect_args['port']
    import MySQLdb
    return MySQLdb.connect(**args)

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._MySQLdbConnection decorator>: ' + repr(self.dbconnection)

  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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


class _OracleConnection(Connection):
  '''A specialization class for cx_Oracle connections'''
  def __init__(self, args):
    Connection.__init__(self, args)
    self._tablenames = None

  def _open_connection(self):
    '''Helper method that opens a connection to the database'''
    import cx_Oracle
    return cx_Oracle.connect(self._connect_args['username'], self._connect_args['password'], self._connect_args['dsn'])

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._OracleConnection decorator>: ' + repr(self.dbconnection)

  def _set_table_types(self, cursor, table):
    '''Helper method for Connection.table().  After the query is run, this method
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
###   by Connection.cursor() and other methods in
###   Connection.

class _Cursor:
  '''A database cursor.  Since Picalo automatically manages cursors,
     you don't need to create these directly.  You can call any method
     on the cursor that you could call on the underlying object.
  '''
  def __init__(self, parent, dbcursor):
    self.dbcursor = dbcursor
    self.parent = parent
    self.columns_map = {}
    
    
  def __getattr__(self, key):
    '''Returns the given attribute of the class.  This is customized so that
       calls to cursor.description and cursor.rowcount are passed to the 
       embedded dbcursor and returned.  This allows you to call
       cursor.rowcount, cursor.description, cursor.fetchone(), and
       all the other cursor methods.
    '''
    # since __getattribute__ is already called, we only get here if 
    # one of our members didn't match the name. Redirect to dbcursor.
    return getattr(self.dbcursor, key)


  def execute(self, sql, parameters=None):
    '''Executes the given sql'''
    assert isinstance(sql, types.StringTypes), 'Invalid SQL string: ' + str(sql)
    if parameters == None:
      self.dbcursor.execute(sql)
    else:
      self.dbcursor.execute(sql, parameters)
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
      
      
  def __iter__(self):
    '''Returns an iterator to the most recent results'''
    while True:
      rec = self.fetchone()
      if rec == None:
        return
      yield rec    
    

  def __str__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Cursor decorator>: ' + str(self.dbcursor)
    

  def __repr__(self):
    '''Returns a string representation of this connection'''
    return '<Picalo Database._Cursor decorator>: ' + repr(self.dbcursor)



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
     Connection.update_query_builder() for more information."""
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
     Connection.insert_query_builder() for more information."""
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
     Connection.select_query_builder() for more information."""
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
    


  
  
  
################################################
###   Query object

class Query(persistent.Persistent):
  '''Represents a query on a database.'''
  def __init__(self, connection, sql, parameters=None, execute=True):
    '''Creates a new query object.  Note that this method is not normally called
       directly.  Instead, call Connection.create_query() so the query can be
       added to the connection and available later.
    
       @param connection:    The connection that this Query will be part of.
       @type  connection:    Connection
       @param sql:           The SQL string to execute.
       @type  sql:           string
       @param parameters:    The parameters to be sent to the database.
       @type  parameters:    List or Tuple
       @param execute:       Whether to execute this query, making the results immediately available.
       @type  execute:       boolean
    '''
    assert sql, 'The sql parameter cannot be empty.'
    assert isinstance(sql, types.StringTypes), 'The sql parameter must be an SQL string.'
    self._connection = connection
    self._table = None
    self.set_sql(sql, parameters, execute)  # adds more class variables, see this method


  def set_sql(self, sql, parameters=None, execute=True):
    '''Modifies the sql of this query, potentially re-executing it with the given connection'''
    self._modified = True
    self._sql = sql
    self._parameters = parameters
    if execute:
      self.execute()
    
    
  def get_sql(self):
    '''Returns the SQL for this query'''
    return self._sql


  def execute(self):
    '''Run the query using the given database connection.'''
    # check the parameter
    cursor = self._connection.cursor()
    
    # run the query
    cursor.query(self._sql, self._parameters)
    assert cursor.description != None, 'You must first run a query that returns results to create a Table object!'
    
    # if the table currently exists, notify that it will be changing
    if self._table != None:
      self._table._notify_listeners(level=3)
    
    # first create the table
    self._table = Table(picalo.make_unique_colnames(picalo.ensure_valid_variables([ desc[0] for desc in cursor.description ])))
    
    # set the types
    cursor.parent._set_table_types(cursor, self._table)
    
    # set up the table data
    for row in cursor:
      self._table.append(row)
    
  
  def is_changed(self):
    '''Returns whether the table has been changed since loading'''
    return self._modified
    
    
  def view(self):
    '''Opens a spreadsheet-view of the table if Picalo is being run in GUI mode.
       If Picalo is being run in console mode, it redirects to prettyprint().
       This is the preferred way of viewing the data in a table.
    '''
    # this is explicitly included in the class so it runs even if the table
    # hasn't been loaded.  the GUI will execute automatically.
    picalo.TableModule.view(self)
    

  def __eq__(self, other):
    '''Returns whether the data in this query are the same as the data in another query/table.'''
    if self._table != None and isinstance(other, Table):
      return self._table == other
    if self._table != None and isinstance(other, Query):
      return self._table == other._table
    return id(self) == id(other)
    

  def is_readonly(self):
    '''Queries are always read-only, so this method always
       returns True.  Use an INSERT or UPDATE query to modify
       database records.
    '''
    return True
    
    
  def set_readonly(self, readonly):
    '''This method throws an error.  The read-only status of Queries
       cannot be changed.'''
    raise AssertionError('The read-only status of Query objects cannot be changed.')   
  
  

  ###############################################################
  ###   List-like methods (won't go through __getattribute__)
  
  def __len__(self):
    assert self._table != None, 'You must first execute the query before accessing its data and methods.'
    return self._table.__len__()
    
  def __getitem__(self, i):
    assert self._table != None, 'You must first execute the query before accessing its data and methods.'
    return self._table.__getitem__(i)
    
  def __iter__(self):
    assert self._table != None, 'You must first execute the query before accessing its data and methods.'
    return self._table.__iter__()
    
    
  ################################################
  ###   Pass-through most methods to Table    
    
  def __getattribute__(self, name):
    # I've overridden __getattribute__ because persistent.Persistent.__getattribute__
    # incorrectly calls str(self) if the attribute is not found in the __dict__ of the
    # object.  In other words, __getattr__ never gets called as it should.
    # first search our own dictionary
    if object.__getattribute__(self, '__dict__').has_key(name):
      return object.__getattribute__(self, '__dict__')[name]
    # next search the superclass
    try:
      return persistent.Persistent.__getattribute__(self, name)
    except AttributeError:
      pass
    # next search the table object
    if object.__getattribute__(self, '__dict__').has_key('_table'):
      assert object.__getattribute__(self, '_table') != None, 'You must first execute the query before calling "%s"' % (name, )
      return getattr(object.__getattribute__(self, '_table'), name)
    # if we get here, it wasn't in any of the three, so throw the attribute error
    raise AttributeError("object of type 'Query' has no atribute named '%s'" % name)
