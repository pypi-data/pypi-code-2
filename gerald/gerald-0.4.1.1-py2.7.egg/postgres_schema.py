#!/usr/bin/python
"""
Introduction
============
  Capture, document and manage PostgreSQL database schemas.

  This is the PostgreSQL Schema module, every class is subclassed from the ones 
  in schema. 

  A schema is comprised of collections of tables, views, stored code objects, 
  triggers, sequences, and other assorted 'objects'

  to create a new schema object from an existing database schema you will need 
  to do something like;

  >>> from gerald import PostgresSchema
  >>> my_schema = PostgresSchema('my_schema', 'postgres:/user:passwd@host/db')

  N.B. the name you specify (e.g. 'my_schema') will be used in all database
  introspection operations. The default PostgreSQL schema name is 'public'.

  If you don't specify a connection string you'll get an empty schema object.

  >>> from gerald import PostgresSchema
  >>> my_schema = PostgresSchema('my_schema')

  With many grateful thanks to 
  http://www.alberton.info/postgresql_meta_info.html for most of the 
  introspection SQL

Meta-Data
=========
  Module  : postgres_schema.py

  License : BSD License (see LICENSE.txt)

Known limitations
=================
  Currently only a minimal implementation supporting Tables, Views and Triggers
"""
__author__ = "Andy Todd <andy47@halfcooked.com>"
__date__ = (2009, 8, 12)
__version__ = (0, 4, 1)

import re
import sys

from gerald import schema

LOG = schema.LOG

DATE_DATATYPES = ('date', 'timestamp', 'time', 'interval', 'timestamp without time zone')
TEXT_DATATYPES = ('character varying', 'character', 'char', 'varchar')
NOLENGTH_DATATYPES = ('text', 'boolean')
NUMERIC_DATATYPES = ('integer', 'int', 'number', 'real', 'smallint', 
                     'numeric', 'decimal')
DEFAULT_NUM_LENGTH = '38'

# Regular expressions for chopping up index ddl in _get_table
TYPE_RE = re.compile('\sUSING\s(\w*)') # The word after 'USING'
UNIQUE_RE = re.compile('UNIQUE')
COL_RE = re.compile('\((.*)\)') # Everything between ( and )

class Schema(schema.Schema):
    """
    A representation of a PostgreSQL database schema

    A PostgreSQL schema is all of the objects owned by a particular user
    """
    def _get_schema(self, cursor):
        """
        Get definitions for the objects in the current schema
        
        We query the data dictionary for (in order);
          - Tables, Views, Sequences (although the last goes nowhere)
        We should also get;
          - Grants, Code objects, DB links and synonyms 

        @param cursor: The cursor to use to query the data dictionary
        @type cursor: Database cursor object
        @return: All of the objects in this schema
        @rtype: Dictionary
        """
        LOG.info('Getting details for PostgreSQL schema %s from database' % self.name)
        schema = {}
        # Tables
        stmt = """SELECT table_name
                  FROM   information_schema.tables
                  WHERE  table_schema = %(schema)s
                  AND    table_type = 'BASE TABLE'"""
        cursor.execute(stmt, {'schema': self.name})
        for table in cursor.fetchall():
            LOG.debug("Getting details for table %s" % table[0])
            schema[table[0]] = Table(table[0], cursor, self.name)
        # Views
        stmt = """SELECT table_name 
                  FROM   information_schema.views
                  WHERE  table_schema = %(schema)s"""
        cursor.execute(stmt, {'schema': self.name})
        for view in cursor.fetchall():
            LOG.debug("Getting details for view %s" % view[0])
            schema[view[0]] = View(view[0], cursor)
        # Sequences - not currently supported for PostgreSQL
        stmt = """SELECT relname 
                  FROM pg_class 
                  WHERE relkind = 'S' 
                  AND relnamespace IN ( SELECT oid 
                                        FROM   pg_namespace 
                                        WHERE  nspname = %(schema)s )"""
        #cursor.execute(stmt, {'schema': self.name})
        #for sequence in cursor.fetchall():
        #    log.debug("Getting details for sequence %s" % sequence[0])
        #    schema[sequence[0]] = Sequence(sequence[0], cursor)
        # Code objects (packages, procedures and functions)
        # Currently not implemented for PostgreSQL
        # Database links. You know, I don't think PostgreSQL has db links
        # All done, return the fruit of our labours
        LOG.info('Got details for schema %s from database' % self.name)
        return schema


class PostgresCalcPrecisionMixin(object):
    """Class to contain the calc_precision static method to be used as a 
    mixin by other classes in this module.
    """

    def calc_precision(data_type, data_length, data_precision=None, data_scale=None):
        """
        Calculate and then return the precision of this column
        
        This is a bit of a hack and will be replaced when columns become 
        first class objects.

        @param data_type: The data type of the column
        @type data_type: String
        @param data_length: The length of the column, if this is present its 
        usually the only numeric value provided
        @type data_length: Integer
        @param data_precision: The total number of digits in the column
        @type data_precision: Integer
        @param data_scale: The number of digits after the decimal point
        @type data_scale: Integer
        @return: The appropriate precision values for this column
        @rtype: String
        """
        if data_type:
            data_type = data_type.lower()
            if data_type in TEXT_DATATYPES:
                if data_length > 0:
                    precision = '(%d)' % int(data_length)
                else:
                    raise ValueError, 'data length must be greater than 0'
            elif data_type in NUMERIC_DATATYPES:
                if data_precision:
                    precision = '(%d' % int(data_precision)
                    if data_scale:
                        precision += ',%d' % int(data_scale)
                    precision += ')'
                else:
                    precision = '(%d)' % DEFAULT_NUM_LENGTH
            elif data_type in DATE_DATATYPES or data_type in NOLENGTH_DATATYPES:
                precision = ""
            else:
                raise ValueError, '%s is not a valid data type' % data_type
        else:
            raise ValueError, 'No data type supplied'
        return precision

    calc_precision = staticmethod(calc_precision)


class Table(schema.Table, PostgresCalcPrecisionMixin):
    """
    A representation of a database table.
    
    A table is made up of columns and may also have indexes, triggers, a primary 
    key and foreign keys.
    """
    def _get_table(self, cursor):
        """
        Query the data dictionary for this table
        
        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        # Tablespace information
        stmt = """SELECT tablespace FROM pg_tables WHERE tablename=%(table)s"""
        table = self.name
        schema = self.schema
        cursor.execute(stmt, locals())
        result = cursor.fetchone()
        if result is None:
            raise AttributeError, "Can't get DDL for table %s" % self.name
        self.tablespace_name = result[0]
        # Columns
        stmt = """SELECT ordinal_position, column_name, data_type, 
                         character_maximum_length, numeric_precision, 
                         numeric_scale, is_nullable, column_default 
                  FROM   information_schema.columns 
                  WHERE  table_name=%(table)s
                  AND    table_schema=%(schema)s
                  """
        cursor.execute(stmt, locals())
        LOG.debug('Getting column details for %s' % self.name)
        for row in cursor.fetchall():
            # Varchar columns are returned as 'character varying'
            new_col = {'sequence': row[0], 'name': row[1]}
            if row[2] == 'character varying':
                new_col['type'] = 'varchar'
            else:
                new_col['type'] = row[2]
            new_col['length'] = row[3]
            new_col['precision'] = row[4]
            new_col['scale'] = row[5]
            if row[6] == 'YES':
                new_col['nullable'] = True
            else:
                new_col['nullable'] = False
            if row[7]:
                new_col['default'] = row[7]
            self.columns[new_col['name']] = new_col
        # Constraints
        stmt = """SELECT constraint_name, 
                         CASE constraint_type
                            WHEN 'PRIMARY KEY' THEN 'Primary'
                            WHEN 'FOREIGN KEY' THEN 'Foreign'
                            WHEN 'CHECK' THEN 'Check'
                            WHEN 'UNIQUE' THEN 'Unique'
                         END AS constraint_type
                  FROM   information_schema.table_constraints
                  WHERE  table_name=%(table)s
                  AND    table_schema=%(schema)s
                  AND    constraint_name NOT LIKE '%%not_null'"""
        cursor.execute(stmt, locals())
        cons_details_stmt = """
              SELECT tc.constraint_name, tc.constraint_type,
                     kcu.column_name, ccu.table_name AS references_table,
                     ccu.column_name AS references_field,
                     rc.unique_constraint_name AS references_constraint
              FROM   information_schema.table_constraints tc
                     LEFT JOIN information_schema.key_column_usage kcu
                       ON  tc.constraint_catalog = kcu.constraint_catalog
                       AND tc.constraint_schema = kcu.constraint_schema
                       AND tc.constraint_name = kcu.constraint_name
                     LEFT JOIN information_schema.referential_constraints rc
                       ON tc.constraint_catalog = rc.constraint_catalog
                       AND tc.constraint_schema = rc.constraint_schema
                       AND tc.constraint_name = rc.constraint_name
                     LEFT JOIN information_schema.constraint_column_usage ccu
                       ON rc.unique_constraint_catalog = ccu.constraint_catalog
                       AND rc.unique_constraint_schema = ccu.constraint_schema
                       AND rc.unique_constraint_name = ccu.constraint_name
              WHERE  tc.table_name = %(table)s
              AND    tc.table_schema = %(schema)s
              AND    tc.constraint_name = %(constraint_name)s
        """
        LOG.debug('Getting constraint details for %s' % self.name)
        for row in cursor.fetchall():
            # Note that Postgres doesn't have the concept of enabled or disabled
            # constraints so we hard code enabled
            constraint = { 'name': row[0], 'type': row[1], 'enabled': True}
            LOG.debug('Getting details for constraint %s' % constraint['name'])
            cursor.execute(cons_details_stmt, {'table':table, 'schema':schema, 'constraint_name':constraint['name']})
            cons_details = cursor.fetchall()
            if constraint['type'] in ('Primary', 'Foreign'):
                constraint['columns'] = [x[2] for x in cons_details]
                if constraint['type'] == 'Foreign':
                    # Third element is reference constraint name
                    ## self.constraints[constraint_name].append('')
                    # Fourth element is reference table
                    ## ref_table = cons_details[0][3]
                    constraint['reftable'] = cons_details[0][3]
                    constraint['refpk'] = cons_details[0][5]
                    ## self.constraints[constraint_name].append(ref_table)
                    # Fourth element is reference columns and if we aren't the
                    # owner it will be None so we try and fail gracefully
                    constraint['refcolumns'] = [x[4] or '' for x in cons_details]
                    ## self.constraints[constraint_name].append(ref_columns)
            if constraint['type'] == 'Check':
                LOG.debug('Getting details for check constraint %s' % constraint['name'])
                stmt = """SELECT check_clause 
                          FROM   information_schema.check_constraints
                          WHERE  constraint_name = %(constraint_name)s
                          AND    constraint_schema = %(constraint_schema)s
                       """
                cursor.execute(stmt, {'constraint_name':constraint['name'], 'constraint_schema':schema})
                results = cursor.fetchone()
                if results:
                    constraint['condition'] = results[0]
                else:
                    constraint['condition'] = ''
            self.constraints[constraint['name']] = constraint
        # Indexes
        stmt = """SELECT oid, relname
                  FROM pg_class
                  WHERE oid IN (
                                SELECT indexrelid
                                FROM pg_index, pg_class
                                WHERE pg_class.relname=%(table)s
                                AND pg_class.oid=pg_index.indrelid
                                AND indisunique != 't' AND indisprimary != 't' 
                               )
        """
        # Columns for an index
        index_ddl_stmt = """SELECT pg_get_indexdef(%(oid)s)"""
        # Get the information
        cursor.execute(stmt, locals())
        LOG.debug('Getting index details for %s' % self.name)
        for index in cursor.fetchall():
            oid, index_name = index
            index_dict = {'name': index_name}
            cursor.execute(index_ddl_stmt, {'oid': oid})
            index_defn = cursor.fetchone()[0]
            # index_defn will now contain valid DDL for the index, we parse it
            # Because the PgSQL data dictionary is incapable of supplying the
            # information we require
            index_dict['type'] = TYPE_RE.search(index_defn).group(1)
            if UNIQUE_RE.search(index_defn):
                index_dict['unique'] = True
            else:
                index_dict['unique'] = False
            index_dict['columns'] = COL_RE.search(index_defn).group(1).split(',')
            self.indexes[index_name] = index_dict
        # Triggers
        stmt = """SELECT trigger_name
                  FROM   information_schema.triggers
                  WHERE  event_object_table = %(table_name)s
                  """
        LOG.debug('Getting trigger details for %s' % self.name)
        cursor.execute(stmt, {'table_name': self.name})
        for trigger in cursor.fetchall():
            trigger_name = trigger[0]
            self.triggers[trigger_name] = Trigger(trigger_name, cursor)

    def get_ddl(self):
        """
        Generate the DDL necessary to create this table in a PostgreSQL database
        
        @return: DDL to create this table 
        @rtype: String
        """
        ddl_strings = [self.get_table_ddl()]
        ddl_strings.append(self.get_constraints_ddl())
        ddl_strings.append(self.get_index_ddl())
        ddl_strings.append(self.get_trigger_ddl())
        return ''.join(ddl_strings)

    def get_table_ddl(self):
        """
        Generate the DDL necessary to create the table and its columns in a
        PostgreSQL database.

        @return: Table DDL
        @rtype: String
        """
        if not hasattr(self, 'name') or self.name == None:
            raise AttributeError, "Table does not have a name"
        ddl_strings = ["CREATE TABLE " + self.name]
        in_columns = False
        cols = self.columns.values()
        cols.sort()
        for column in cols:
            if in_columns:
                ddl_strings.append("\n  ,")
            else:
                ddl_strings.append("\n ( ")
                in_columns = True
            ddl_strings.append(column['name'] + " " + column['type'])
            if 'precision' in column:
                ddl_strings.append(self.calc_precision(column['type'], column['length'], column['precision'], column['scale']))
            elif 'length' in column:
                ddl_strings.append(self.calc_precision(column['type'], column['length']))
            else:
                ddl_strings.append(column['type'])
            # Nullable?
            if not column['nullable']:
                ddl_strings.append(" NOT NULL")
        if len(ddl_strings) > 1:
            ddl_strings.append(" );")
        return "".join(ddl_strings)

    def get_named_constraint_ddl(self, constraint_name):
        """
        Generate the DDL for the constraint named constraint_name

        @parameter constraint_name: The name of a constraint
        @type constraint_name: String
        @return: DDL to create a constraint
        @rtype: String
        """
        ddl_strings = []
        if constraint_name in self.constraints:
            cons_details = self.constraints[constraint_name]
            cons_type = cons_details['type']
            ddl_strings.append('ALTER TABLE %s ADD ' % self.name)
            ddl_strings.append('CONSTRAINT %s' % constraint_name)
            if cons_type == 'Check':
                ddl_strings.append(' CHECK ( %s )' % cons_details['condition'])
            elif cons_type == 'Primary':
                ddl_strings.append(' PRIMARY KEY (')
            elif cons_type == 'Foreign':
                ddl_strings.append(' FOREIGN KEY (')
            if cons_type in ('Primary', 'Foreign'):
                ddl_strings.append(', '.join(cons_details['columns']))
                ddl_strings.append(')')
            if cons_type == 'Foreign':
                ddl_strings.append(" REFERENCES %s (" % cons_details ['reftable'])
                # Add the columns separated by commas
                ddl_strings.append(', '.join(cons_details ['refcolumns']))
                ddl_strings.append(")")
            ddl_strings.append(';\n')
        return ''.join(ddl_strings)

    def get_constraints_ddl(self):
        """
        Generate the DDL for all of the constraints defined against this table
        in PostgreSQL database syntax.

        @return: DDL to create zero, one or more constraints
        @rtype: String
        """
        ddl_strings = ['']
        for constraint in self.constraints:
            ddl_strings.append(self.get_named_constraint_ddl(constraint))
        return ''.join(ddl_strings)

    def get_index_ddl(self):
        """
        Generate the DDL necessary to create indexes defined against this table 
        in a PostgreSQL database
        
        @return: DDL to create the indexes for this table 
        @rtype: String
        """
        ddl_strings = []
        for index_name, index_details in self.indexes.items():
            ddl_strings.append('CREATE')
            # Only put the uniqueness if the index is actually unique
            # if index[1] != 'NONUNIQUE':
            #     ddl_strings.append(' %s' % index[1])
            ddl_strings.append(' INDEX %s ON %s' % (index_name, self.name))
            ddl_strings.append(' ( %s );\n' % ','.join(index_details['columns']))
        return "".join(ddl_strings)

    def get_trigger_ddl(self):
        """
        Generate the DDL necessary to create any triggers defined against this
        table in a PostgreSQL database.

        @return: DDL to create triggers
        @rtype: String
        """
        ddl_strings = []
        for trigger in self.triggers:
            ddl_strings.append('\n')
            ddl_strings.append(self.triggers[trigger].get_ddl())
        return "".join(ddl_strings)


class View(schema.View, PostgresCalcPrecisionMixin):
    """
    A representation of a database view.

    A View is made up of columns and also has an associated SQL statement.
    
    Most of the methods for this class are inherited from schema.View
    """
    view_sql = {
      'text': """SELECT view_definition 
                 FROM information_schema.views 
                 WHERE table_name=%(name)s""",
      'columns': """SELECT 0, cols.column_name,
                           (CASE WHEN cols.data_type='character varying' 
                                 THEN 'varchar'
                                 ELSE cols.data_type END) AS data_type,
                           cols.character_maximum_length, cols.numeric_precision, 
                           cols.numeric_scale, cols.is_nullable
                    FROM   information_schema.view_column_usage vcu
                           JOIN information_schema.columns cols ON 
                             (vcu.table_name=cols.table_name AND 
                              vcu.column_name=cols.column_name)
                    WHERE  view_name=%(name)s""",
      'triggers': """SELECT trigger_name 
                     FROM information_schema.triggers 
                     WHERE table_name=%(name)s""",
    }


    def _get_view(self, cursor):
        """
        Query the data dictionary for this view

        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        arguments = { 'name': self.name, }
        LOG.debug('Getting definition of view %s' % self.name)
        cursor.execute(self.view_sql['text'], arguments)
        # If we don't own the view this will be None
        self.sql = cursor.fetchone()[0] or ''
        # Columns
        cursor.execute(self.view_sql['columns'], arguments)
        row_sequence = 0
        for col_row in cursor.fetchall():
            row_sequence += 1
            col_name = col_row[1]
            self.columns[col_name] = {'sequence': row_sequence, 'name': col_name }
            self.columns[col_name]['type'] = col_row[2]
            self.columns[col_name]['length'] = col_row[3]
            self.columns[col_name]['precision'] = col_row[4]
            self.columns[col_name]['scale'] = col_row[5]
            if col_row[6] == 'YES':
                self.columns[col_name]['nullable'] = True
            else:
                self.columns[col_name]['nullable'] = False
        # Triggers - to be implemented, something like;
        """
        ::

          cursor.execute(self.view_sql['triggers'], arguments)
          for trigger in cursor.fetchall():
              trigger_name = trigger[0]
              self.triggers[trigger_name] = Trigger(trigger_name, cursor)
        """

    def get_ddl(self):
        """
        Generate the DDL necessary to create this view

        @return: DDL to create this view
        @rtype: String
        """
        if not hasattr(self, 'name') or self.name == None:
            raise AttributeError, "Can't generate DDL for a view without a name"
        ddl_strings = ["CREATE VIEW "+self.name]
        in_columns = False
        # The columns may not necessarily be in the correct order. So we make a 
        # copy and sort by the first element of the tuple - the column number
        columns = self.columns.values()
        columns.sort()
        for col in columns:
            if in_columns:
                ddl_strings.append(" \n ,")
            else:
                ddl_strings.append(" ( ")
                in_columns = True
            ddl_strings.append(col['name'])
        # Only close the columns clause if we've actually got any columns
        if in_columns:
            ddl_strings.append(") AS\n  ")
        # Should strip excessive white space from self.sql before appending it 
        ddl_strings.append(self.sql)
        return "".join(ddl_strings)
        

class Trigger(schema.Trigger):
    """
    A representation of a database trigger.

    A trigger has triggering events and a SQL statement. A trigger can only
    exist within the context of a table or view and thus doesn't need any table 
    references as you can get those from its parent. Apart from the table or 
    view name, of course, which we need within the get_ddl method.

    Most of the methods for this class are inherited from schema.Trigger
    """
    def _get_trigger(self, cursor):
        """
        Query the data dictionary for this trigger
        
        @param cursor: All of the select statements will be executed using this
          cursor.
        @type cursor: Database cursor object
        """
        stmt = """SELECT action_orientation, event_manipulation, 
                         action_statement, event_object_table
                  FROM   information_schema.triggers 
                  WHERE  trigger_name = %(trigger_name)s""" 
        cursor.execute(stmt, {'trigger_name': self.name})
        LOG.debug('Getting details of trigger %s' % self.name)
        results = cursor.fetchone()
        self.type, self.events, self.sql, self.table_name = results
        self.level = self.type

    def get_ddl(self):
        """
        Generate the DDL necessary to create this trigger

        @return: DDL to create this trigger
        @rtype: String
        """
        if not hasattr(self, 'scope') or not hasattr(self, 'level') or len(self.events) == 0 or not hasattr(self, 'sql'):
            raise ValueError, 'Cannot generate ddl for trigger %s' % self.name
        ddl_strings = ['CREATE OR REPLACE TRIGGER %s' % self.name]
        ddl_strings.append(' %s %s ' % (self.type, self.events))
        ddl_strings.append('ON %s\n' % self.table_name)
        if self.level:
            ddl_strings.append(' FOR %s\n' % self.level)
        ddl_strings.append(self.sql)
        ddl_strings.append('\n/\n')
        return "".join(ddl_strings)


if __name__ == "__main__":
    print "This module should not be invoked from the command line"
    sys.exit(1)
