####################################################################################
#                                                                                  #
# Copyright (c) 2006 Dr. Conan C. Albrecht <conan_albrechtATbyuDOTedu>             #
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
#                                                                                  #
#  This file is globally imported into Picalo.  See picalo/__init__.py.            # 
#  When you write "from picalo import *", these functions all get imported.        #
#                                                                                  #
####################################################################################

from picalo import check_valid_table
from Error import error
from Table import Table
import types, os, os.path
import transaction
import ZODB.DB
import ZODB.FileStorage.FileStorage
import persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList

# global functions (defined in this file)
__all__ = [
  'Project',
  'open_project',
  'save_project',
  'close_project',
  'delete_project',
]


####################################################################
###   Open, save, delete project.

def open_project(filename, cache_size=2000):
  '''Opens a project file in the workspace.  If the project does not yet exist,
     it is created.
  
     @param filename:   The filename the project will be stored in.
     @type  filename:   str
     @param cache_size: The number of objects (tables, records, columns, etc.) to keep in memory at any given time.
     @type  cache_size: int
     @return:           A Picalo project
     @rtype:            Project
  '''
  return Project(filename, cache_size)
  

def save_project(project):
  '''Saves an open project.  This is a funcational alternative to
     project.save().'''
  project.save()
  
  
def close_project(project):
  '''Saves and closes a project, freeing any memory it is using.
     This is a funcational alternative to project.close().
  '''
  project.close()
  

def delete_project(filename):
  '''Removes the given project along with its associated indices and lock files.  The files
     and data within them are permanently removed from disk.'''
  assert isinstance(filename, types.StringTypes), 'Please enter a valid filename.'
  assert os.path.exists(filename), 'Project with filename %s does not exist.' % filename
  for ext in ( '', '.index', '.lock', '.tmp', '.old' ):
    if os.path.exists(filename + ext):
      os.remove(filename + ext)
  


####################################################################
###   Represents a Picalo project.  All data in Picalo are
###   kept in a project, and internally, it uses the Zope DB
###   to store everything.



class Project:
  '''A top-level Picalo project.  All tables, database connections, queries,
     and other project settings are kept in a Project.  Picalo projects
     normally have the .pcp extension.
  '''
  def __init__(self, filename, cache_size=2000):
    '''Links to a project file on disk.  If the file does not exist, it 
       is created.
       
       @param filename:   The filename the project will be stored in.
       @type  filename:   str
       @param cache_size: The number of objects (tables, records, columns, etc.) to keep in memory at any given time.
       @type  cache_size: int
       @return:           A Picalo project
       @rtype:            Project
    '''
    assert filename, 'Please specify a filename for this project.'
    assert isinstance(filename, types.StringTypes), 'Please specify a valid filename for this project.'
    assert isinstance(cache_size, (int, long)), 'Please specify an integer for the cache size.'
    
    # open the database
    self.filename = filename
    self.transaction_manager = transaction.TransactionManager()
    self.zodb = ZODB.DB(ZODB.FileStorage.FileStorage(filename), cache_size=cache_size)
    self.root = self.zodb.open(self.transaction_manager).root()
    
    # ensure we have the necessary elements for a Picalo project in the file
    if not self.root.has_key('Settings'):
      self.root['Settings'] = PersistentDict()
    if not self.root.has_key('Tables'):
      self.root['Tables'] = PersistentDict()
    if not self.root.has_key('DatabaseConnections'):
      self.root['DatabaseConnections'] = PersistentDict()
    if not self.root.has_key('Queries'):
      self.root['Queries'] = PersistentDict()
    
    
  def close(self):
    '''Closes the project file, automatically saving changes'''
    self.save()
    self.zodb.close()
    

  def save(self):
    '''Saves any changes to this project to disk.'''
    self.transaction_manager.commit()
    
    
  def abort(self):
    '''Restores the project to the state it was in when it was opened or just after the last save
       point, whichever is later.  All changes to the project, including its tables and information
       are lost.'''
    self.transaction_manager.abort()
    
    
  def pack(self):
    '''Packs the project to reduce its size on disk.  To make operations faster,
       Picalo files continue to grow over time, even when records and tables are 
       deleted.  Packing a project periodically ensures it doesn't become
       abnormally large.  Note that packing does not do any error correction in the
       file -- it simply removes any redundancies and deleted items.
       
       The following are done to pack a file:
        - Deleted records are permanently removed from their tables.
        - Deleted tables are permanently removed from the project.
    '''
    self.zodb.pack()
    
    
  def __str__(self):
    '''Prints a string representation of this project'''
    return '[Picalo Project: %s tables, %s database connections, %s queries]' % (len(self.root['Tables']), len(self.root['DatabaseConnections']), len(self.root['Queries']))
    
    
  def __getattr__(self, name):
    '''Retrieves a member of this project by name.  The order of search for the
       name is Project methods, tables, database connections, queries.
       
       Example:
         >>> # assume we have a project with a tabled named "mydata"
         >>> project.mydata.view()
         >>>
         >>> # alternatively:
         >>> project.get_table('mydata')
       
       @param col: The column name or index
       @type  col: str
       @return:    The value in the given field
       @rtype:     returns
    '''
    for node in [ 'Tables', 'DatabaseConnections', 'Queries' ]:
      if self.root[node].has_key(name):
        return self.root[node][name]
    raise AttributeError, 'Project has no item named "%s".' % name
    
      
    
  #########################################
  ###   Table methods
  
  def add_table(self, name, table):
    '''Adds a Picalo Table, TableList, or TableArray to this project.  When this
       project is saved, the table will be saved with it.  This method is the 
       primary way to create and save tables in Picalo.
       
       Don't forget to call project.save() to make the change permanent.
       
       Example 1:
       >>> # creates a table with two columns and adds to the project
       >>> data = project.add_table('data', Table([id, name])
       >>>
       
       Example 2:
       >>> # creates a table with two columns and assigns to a local variable, then adds to the project
       >>> table = Table([id, name])
       >>> project.add_table('data', table)
       >>>
       
       @param name:      A name the table will be known by in this project.
       @type  name:      str
       @param table:     The table variable (Example 2) or table creation statement (Example 1)
       @type  table:     Table, TableList, or TableArray
       @return:          The Picalo table that was just added (so tables can be created inline as in Example 1)
       @rtype:           Table
    '''
    assert isinstance(name, types.StringTypes) and name != '', 'Please enter a valid name for this table.'
    assert not self.root['Tables'].has_key(name), 'A table in this project already has the name "%s".  Please delete it first.' % name
    self.root['Tables'][name] = table


  def get_table(self, name):
    '''Returns a reference to a table with the given name.  Tables can also be referenced directly,
       as in project.tablename.
       
       @param name:      The name of the table within this project.
       @type  name:      str
       @return:          The Picalo table.
       @rtype:           Table, TableList, or TableArray
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this table.'
    assert self.root['Tables'].has_key(name), 'Table with name "%s" not found in the project.' % name
    return self.root['Tables'][name]
    
    
  def has_table(self, name):
    '''Returns whether this project has a table with the given name.
    
       @param name:      The name of the table within this project.
       @type  name:      str
       @return:          True if the table exists, False otherwise.
       @rtype:           boolean
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this table.'
    return self.root['Tables'].has_key(name)
    
    
  def list_tables(self):
    '''Returns an alphabetical list of tables in this project.

       @return:                   A list of table names.
       @rtype:                    list of str
    '''
    names = self.root['Tables'].keys()
    names.sort()
    return names
    
    
  def remove_table(self, name):
    '''Removes the table with the given name from the project.  
    
       If you have a local variables pointing to the table, 
       you still have full access to the table.  This method just removes 
       the table from the project file.  If no more variables point to the
       table, it is premanently deleted.

       Don't forget to call project.save() to make the change permanent.  
       Call project.pack() to free the space used by the removed table and 
       make the project file smaller on disk.

       @param name:      The name of the table within this project.
       @type  name:      str
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this table.'
    assert self.root['Tables'].has_key(name), 'Table with name "%s" not found in the project.' % name
    del self.root['Tables'][name]
    

  #########################################
  ###   Database Connection methods
   
  def add_database_connection(self, name, dbconn):
    '''Adds a Picalo Database Connection to this project.  When this
       project is saved, the connection will be saved with it.  This method is the 
       primary way to create and save database connections in Picalo.
       
       Don't forget to call project.save() to make the change permanent.
       
       Example 1:
       >>> # creates a database connection to SQLite3
       >>> sq3conn = project.add_database_connection('sq3conn', Database.SqliteConnection("/mydir/mydb.sqlite3"))
       >>>
       
       Example 2:
       >>> # creates a database connection to MySQL, then adds to the project
       >>> mysqlconn = Database.MySQLConnection('mydatabase', 'myuser', 'mypassword', 'localhost')
       >>> project.add_database_connection('mysqlconn', mysqlconn)
       >>>
       
       @param name:      A name the connection will be known by in this project.
       @type  name:      str
       @param dbconn:    The database connection variable (Example 2) or database connection creation statement (Example 1)
       @type  dbconn:    Database.Connection
       @return:          The Picalo connection that was just added (so connections can be created inline as in Example 1)
       @rtype:           Database.Connection
    '''
    assert isinstance(name, types.StringTypes) and name != '', 'Please enter a valid name for this database connection.'
    assert not self.root['DatabaseConnections'].has_key(name), 'A database connection in this project already has the name "%s".  Please delete it first.' % name
    self.root['DatabaseConnections'][name] = dbconn


  def get_database_connection(self, name):
    '''Returns a reference to a database connection with the given name.  Database connections
       can also be referenced directly, as in project.connectionname.
       
       @param name:      The name of the database connection within this project.
       @type  name:      str
       @return:          The database connection
       @rtype:           Database.Connection
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this database connection.'
    assert self.root['DatabaseConnections'].has_key(name), 'Database connection with name "%s" not found in the project.' % name
    return self.root['DatabaseConnections'][name]
    
    
  def has_database_connection(self, name):
    '''Returns whether this project has a database connection with the given name.
    
       @param name:      The name of the database connection within this project.
       @type  name:      str
       @return:          True if the connection exists, False otherwise.
       @rtype:           boolean
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this database connection.'
    return self.root['DatabaseConnections'].has_key(name)
    
    
  def list_database_connections(self):
    '''Returns an alphabetical list of database connetions in this project.

       @return:                   A list of database connection names.
       @rtype:                    list of str
    '''
    names = self.root['DatabaseConnections'].keys()
    names.sort()
    return names
    
    
  def remove_database_connection(self, name):
    '''Removes the database connection with the given name from the project.  
    
       If you have a local variables pointing to the connection, 
       you still have full access to the connection.  This method just removes 
       the connection from the project file.  If no more variables point to the
       connection, it is premanently deleted.

       Don't forget to call project.save() to make the change permanent.  

       @param name:      The name of the database connection within this project.
       @type  name:      str
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this database connection.'
    assert self.root['DatabaseConnections'].has_key(name), 'Database connection with name "%s" not found in the project.' % name
    del self.root['DatabaseConnections'][name]
    


  #########################################
  ###   Query methods
  
  def add_query(self, name, query):
    '''Adds a Picalo Query to this project.  When this
       project is saved, the query will be saved with it.  This method is the 
       primary way to create and save database queries in Picalo.
       
       Don't forget to call project.save() to make the change permanent.
       
       Example 1:
       >>> # creates a query
       >>> myquery = project.add_query(Database.Query("SELECT * FROM mytable"))
       >>>
       
       Example 2:
       >>> # creates a query, then adds to the project
       >>> myquery = Database.Query("SELECT * FROM mytable")
       >>> project.add_query('myquery', myquery)
       >>>
       
       @param name:      A name the query will be known by in this project.
       @type  name:      str
       @param query:     The query variable (Example 2) or query creation statement (Example 1)
       @type  query:     Database.Query
       @return:          The Picalo query that was just added (so queries can be created inline as in Example 1)
       @rtype:           Database.Query
    '''
    assert isinstance(name, types.StringTypes) and name != '', 'Please enter a valid name for this query.'
    assert not self.root['Queries'].has_key(name), 'A query in this project already has the name "%s".  Please delete it first.' % name
    self.root['Queries'][name] = query


  def get_query(self, name):
    '''Returns a reference to a query with the given name.  Database queries
       can also be referenced directly, as in project.queryname.
       
       @param name:      The name of the query within this project.
       @type  name:      str
       @return:          The query
       @rtype:           Database.Query
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this query.'
    assert self.root['Queries'].has_key(name), 'Query with name "%s" not found in the project.' % name
    return self.root['Queries'][name]
    
    
  def has_query(self, name):
    '''Returns whether this project has a query with the given name.
    
       @param name:      The name of the query within this project.
       @type  name:      str
       @return:          True if the query exists, False otherwise.
       @rtype:           boolean
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this query.'
    return self.root['Queries'].has_key(name)
    
    
  def list_queries(self):
    '''Returns an alphabetical list of queries in this project.

       @return:                   A list of query names.
       @rtype:                    list of str
    '''
    names = self.root['Queries'].keys()
    names.sort()
    return names
    
    
  def remove_query(self, name):
    '''Removes the query with the given name from the project.  
    
       If you have a local variables pointing to the query, 
       you still have full access to the query.  This method just removes 
       the query from the project file.  If no more variables point to the
       query, it is premanently deleted.

       Don't forget to call project.save() to make the change permanent.  

       @param name:      The name of the query within this project.
       @type  name:      str
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this query.'
    assert self.root['Queries'].has_key(name), 'Database query with name "%s" not found in the project.' % name
    del self.root['Queries'][name]
    
