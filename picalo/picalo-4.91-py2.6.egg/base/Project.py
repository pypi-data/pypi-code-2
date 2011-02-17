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

from Global import check_valid_table
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
  'create_project',
  'open_project',
  'save_project',
  'close_project',
  'delete_project',
]


####################################################################
###   Create, open, save, delete project.

def create_project(filename, cache_size=2000):
  '''Creates a new project, erasing any existing projects with 
     the filename.  Picalo projects normally have the .pcp
     extension.

     @param filename:   The filename the project will be stored in.
     @type  filename:   str
     @param cache_size: The number of objects (tables, records, columns, etc.) to keep in memory at any given time.
     @type  cache_size: int
     @return:           A Picalo project
     @rtype:            Project
  '''
  # erase any existing project
  if os.path.exists(filename):
    delete_project(filename)
  
  # create the new one
  return open_project(filename, cache_size)


def open_project(filename, cache_size=2000):
  '''Opens an existing project file in the workspace.
  
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



class Project(persistent.Persistent):
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
    # class methods are already searched before __getattr__ gets called (not true with __setattr__, btw)
    for node in [ 'Tables', 'DatabaseConnections', 'Queries' ]:
      if self.root[node].has_key(name):
        return self.root[node][name]
    
    
      
    
  #########################################
  ###   Table methods
  
  def create_table(self, name, columns=3, data=[]):
    '''Creates a Picalo Table.  Tables are the single-most important item
       in Picalo.  It should be the first place users look to understand
       how to use the program.  See the manual for more information on
       how tables work.
       
       This method is the primary way to create tables in Picalo.  It is
       a convenience method that both creates the table and adds it to a 
       project.  
       
       See the Table() documentation for information on the format of the columns
       and data parameters.
    
       Example 1:
         >>> # create and assign a table to this project
         >>> data = project.create_table('data', ['id', 'name'])
         >>>
         >>> # the above line is equivalent to this:
         >>> data = Table(['id', 'name'])
         >>> project.add_table('data', data)
         >>>
         >>> # make the new table a permanent part of the project
         >>> project.save()

       @param name:      A name the table will be known by in this project.
       @type  name:      str
       @param columns:   A list of (name, type) pairs specifying the column names and their types
       @type  columns:   list
       @param data:      The initial data for the table specified as another Picalo table or a list of lists.
       @type  data:      Table/list
       @return:          The new Picalo table.
       @rtype:           Table
    '''
    assert isinstance(name, types.StringTypes) and name != '', 'Please enter a valid name for this table.'
    assert not self.root['Tables'].has_key(name), 'A table in this project already has the name "%s".  Please delete it first.' % name
    t = Table(columns, data)
    self.root['Tables'][name] = t
    return t
    
    
  def add_table(self, name, table):
    '''Adds an existing Picalo table to this project.  Tables that are created directly
       (with data = Table(...) syntax) are not automatically associated with a project.
       This method adds a table not associated with this project to this project.  When this
       project is saved, the table will be saved with it.
       
       Don't forget to call project.save() to make the change permanent.

       @param name:      A name the table will be known by in this project.
       @type  name:      str
       @return:          The Picalo table.
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
       @rtype:           Table
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
    
       Note that the table data are not removed from memory, so if you still have
       local variables pointing to the table, you still have full access to the 
       data.  This method just removes the table from the project file.

       Don't forget to call project.save() to make
       the change permanent.  Call project.pack() to free the space used by the 
       deleted table and make the project file smaller on disk.

       @param table:      The name of the table within this project.
       @type  table:      str
    '''
    assert isinstance(name, types.StringTypes), 'Please enter a valid name for this table.'
    assert self.root['Tables'].has_key(name), 'Table with name "%s" not found in the project.' % name
    del self.root['Tables'][name]
    
  