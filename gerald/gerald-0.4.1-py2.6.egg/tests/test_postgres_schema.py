#!/usr/bin/python
"""
Introduction
============
  Test suite for postgresSchema module from the gerald framework

  Note that this suite uses the py.test module to run
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  We want to test two different aspects of the postgresSchema module;
    - Reading a schema from a PostgreSQL database 
    - Specifying a schema using the in memory structures

  There will be tests for both of these approaches and hopefully some checking 
  that the two starting points produce the same results.

  To run these tests you must have a PostgreSQL database called 'gerald' with a 
  user called 'gerald' that has a password of 'gerald' running on a server that
  you can access. 

  These connection details should be recorded in URI form in the global variable
  TEST_CONNECTION_STRING

  Tests relying on an existing database will use the EXISTING_CONNECTION_STRING.
  Make sure that this points to a valid schema that contains one or more database
  objects.

  To Do;
    Read the connection strings from a configuration file that is not under
    version control
"""
__date__ = (2009, 7, 24)
__version__ = (0, 4, 1)
__author__ = "Andy Todd <andy47@halfcooked.com>"

import os
import re
from xml.etree import ElementTree

# Imported solely so that we can access the Exception hierarchy
import psycopg2

from gerald import PostgresSchema
from gerald.postgres_schema import Table, View, Trigger
from gerald.schema import Trigger as schema_trigger
from gerald.utilities.dburi import get_connection
import py.test

from gerald.utilities.Log import get_log

LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_postgresschema.log')
log = get_log('test_postgresschema', LOG_FILENAME, 'INFO')

TEST_INSTANCE = ''
try:
    from local_connection_data import PG_TEST_INSTANCE as TEST_INSTANCE
except ImportError:
    pass

TEST_CONNECTION_STRING = 'postgres://gerald:gerald@localhost:5433/gerald'
try:
    from local_connection_data import PG_TEST_CONNECTION_STRING as TEST_CONNECTION_STRING
except ImportError:
    pass

if TEST_INSTANCE:
    TEST_CONNECTION_STRING += '@%s' % TEST_INSTANCE
    
# Make sure this points to an existing, valid, user in a PostgreSQL database 
EXISTING_CONNECTION_STRING = 'postgres://portfolio:portfolio@localhost:5433/portfolio'
try:
    from local_connection_data import PG_EXISTING_CONNECTION_STRING as EXISTING_CONNECTION_STRING
except ImportError:
    pass

class TestSchemaNew(object):
    "Unit test for creating schemas using our Schema class"
    def setup_class(self):
        self.schema_name = 'empty test'

    def test_empty(self):
        "Can we create an empty (in memory) schema"
        self.empty_schema = PostgresSchema(self.schema_name)

    def test_name_attribute(self):
        "Does our schema object have a name attribute?"
        assert PostgresSchema(self.schema_name).name == self.schema_name

    def test_version_attribute(self):
        "Does our schema object have a schema_api_version attribute?"
        assert hasattr(PostgresSchema(self.schema_name), 'api_version')


class TestSchemaAddTable(object):
    "Unit tests for adding a table to a new schema"
    def setup_class(self):
        self.schema_name = 'empty test'
        self.empty_schema = PostgresSchema(self.schema_name)

    def test_new_table(self):
        "Add a table to our empty (in memory) schema"
        self.table_name = 'test_table'
        new_table = Table(self.table_name)
        new_table.columns['col1'] = {'sequence':1, 'name':'col1',
                'type':'VARCHAR', 'length':20, 'nullable':False }
        self.empty_schema.schema[self.table_name] = new_table

    def test_new_table_ddl(self):
        "Make sure that our new schema generates some DDL"
        assert self.empty_schema.get_ddl() != None


class TestSchemaDatabase(object):
    "Unit test for creating schemas from an existing database"

    def setup_class(self):
        "Set up our test connection"
        self.schema_name = 'public'
        self.test_schema = PostgresSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_invalid_connection_string(self):
        "If we try and create a schema using an invalid connection string we should get an exception"
        py.test.raises(psycopg2.OperationalError, PostgresSchema, 'invalid', 'postgres://scot:tigger@localhost')

    def test_simple(self):
        "Test connecting to the 'test' database"
        assert self.test_schema is not None

    def test_dump(self):
        "Does the dump method work on an existing schema?"
        assert self.test_schema.dump() is not None

    def test_name(self):
        "The name of our schema should be the one we provided at initialisation"
        assert self.test_schema.name == self.schema_name

    def test_get_ddl(self):
        "The get_ddl method should return more than an empty string"
        assert self.test_schema.get_ddl() != None

    def test_to_xml(self):
        "The to_xml method should return more than an empty string"
        assert self.test_schema.to_xml() != None

    def test_compare(self):
        "Test that equivalent schemas are indicated as such"
        duplicate_schema = PostgresSchema(self.schema_name, EXISTING_CONNECTION_STRING)
        assert self.test_schema == duplicate_schema


class TestNewTableParent(object):
    def setup_class(self):
        self.table_name = 'test_table'
        self.column_name = 'empty_column'
        self.column = {'sequence': 1, 'name': self.column_name, 'type': 'VARCHAR', 
                  'length': 20, 'nullable': False}


class TestTableNew(TestNewTableParent):
    "Unit tests for creating tables using our Table class"
    def test_empty(self):
        "Can we create an empty (in memory) table?"
        self.empty_table = Table(self.table_name)

    def test_empty_table_get_ddl(self):
        "Can we get valid DDL from this empty table?"
        ddl = Table(self.table_name).get_ddl() 
        assert ddl == 'CREATE TABLE test_table'

    def test_table_without_name(self):
        table = Table('no_name')
        table.name = None
        py.test.raises(AttributeError, table.get_ddl)


class TestTableAddColumns(TestNewTableParent):
    "Unit tests for adding columns to an in memory table"
    def setup_method(self, method):
        self.empty_table = Table(self.table_name)
        
    def test_add_column(self):
        "Can we add a column to our new (in memory) table?"
        self.empty_table.columns[self.column_name] = self.column

    def test_one_column_get_ddl(self):
        "Is the ddl we get back correct?"
        self.empty_table.columns[self.column_name] = self.column
        ddl = self.empty_table.get_ddl()
        log.debug(ddl)
        assert ddl == 'CREATE TABLE test_table\n ( empty_column VARCHAR(20) NOT NULL );'


class TestTableMethods(TestNewTableParent):
    "Unit tests for methods of Table objects"
    def setup_method(self, method):
        self.table = Table(self.table_name)
        self.table.columns[self.column_name] = self.column

    def test_new_table_dump(self):
        table_dump = 'Table : %s\n' % self.table_name
        table_dump += '  %s                   ' % self.column_name
        table_dump += '%s(%s)      NOT NULL\n' % (self.column['type'],
                self.column['length'])
        assert self.table.dump() == table_dump

    def test_new_table_get_ddl(self):
        table_ddl = 'CREATE TABLE %s\n' % self.table_name
        table_ddl += ' ( %s ' % self.column_name
        table_ddl += '%s(%s) NOT NULL );' % (self.column['type'],
                self.column['length'])
        assert self.table.get_ddl() == table_ddl

    def test_table_to_xml(self):
        "Does the to_xml method on the table produce some output"
        assert self.table.to_xml().startswith('<table name="')

    def test_table_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.table.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)

    def test_new_table_to_xml(self):
        table_xml = '<table name="%s">\n  ' % self.table_name
        table_xml += '<column name="%s" data-type="%s" sequence="%s">\n    ' % (self.column_name, self.column['type'], self.column['sequence'])
        table_xml += '<length>%s</length>\n  ' % self.column['length']
        table_xml += '</column>\n</table>'
        assert self.table.to_xml() == table_xml

    def test_new_table_compare(self):
        new_table = Table(self.table_name)
        new_table.columns[self.column_name] = self.column
        assert self.table == new_table


class TestTriggerNew(object):
    "Unit test for creating Trigger objects"
    def setup_class(self):
        self.trigger_name = 'test_table'
        self.scope = 'before'
        self.events = ('update', 'insert', 'delete')
        self.level = 'row'
        self.sql = """
        BEGIN
            null;
        END;
        """

    def test_new_trigger(self):
        "Can we create a trigger object?"
        my_trigger = Trigger(self.trigger_name)

    def test_trigger_no_name(self):
        "We shouldn't be able to create a trigger without a name"
        py.test.raises(TypeError, Trigger)

    def test_empty_ddl(self):
        "An empty trigger should produce valid DDL"
        trigger = Trigger(self.trigger_name)
        py.test.raises(ValueError, trigger.get_ddl)
    
    def test_add_attributes(self):
        "Can we populate the appropriate attributes on an empty Trigger?"
        empty = Trigger(self.trigger_name)
        empty.scope = self.scope
        empty.events = self.events
        empty.level = self.level
        empty.sql = self.sql


class TableFromDbParent(object):
    def setup_class(self):
        "Create our table in the designated database"
        self.table_name = 'test_table_from_db'
        self.schema = 'public'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMERIC(16) NOT NULL 
           ,col2 TEXT
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.commit()


class TestTableFromDb(TableFromDbParent):
    "Unit tests for round tripping a table from the database"
    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor, self.schema)


class TestColumnTypesFromDb(TableFromDbParent):
    "Unit test for different column types"
    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor, self.schema)
        self.num_col = self.table.columns['col1']
        self.text_col = self.table.columns['col2']

    def test_numeric_col_sequence(self):
        "Is the sequence of the numeric column set correctly?"
        assert self.num_col['sequence'] == 1

    def test_numeric_col_type(self):
        "Is the type of the numeric column set correctly?"
        assert self.num_col['type'] == 'numeric'

    def test_numeric_col_nullable(self):
        "Is the nullable attribute of the numeric column correct?"
        assert self.num_col['nullable'] == False

    def test_numeric_col_precision(self):
        "Is the precision of the numeric column set correctly?"
        assert self.num_col['precision'] == 16

    def test_numeric_col_scale(self):
        "Is the scale of the numeric column set correctly?"
        assert self.num_col['scale'] == 0

    def test_text_col_sequence(self):
        "Is the sequence of the text column set correctly?"
        assert self.text_col['sequence'] == 2

    def test_text_col_type(self):
        "Is the type of the text column set correctly?"
        assert self.text_col['type'] == 'text'

    def test_text_col_nullable(self):
        "Is the nullable attribute of the text column correct?"
        assert self.text_col['nullable'] == True


class TestTableFromDbAttributes(TableFromDbParent):
    "Unit tests for attributes and methods of a table read from the database"
    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor, self.schema)

    def test_ddl_round_trip(self):
        """Does the get_ddl method generate equivalent SQL to the original?
        
        This one gets tricky because the strings are never going to be exactly
        the same. So at the moment I simply test for the correct start to the
        returned string.
        """
        ddl = self.table.get_ddl()
        table_re = re.compile('CREATE\sTABLE\s%s' % self.table_name, re.IGNORECASE)
        assert table_re.match(ddl) != None

    def test_table_name(self):
        "Make sure the name attribute of our table is correct"
        assert self.table.name == self.table_name

    def todo_test_tablespace_name(self):
        "Make sure the tablespace_name attribute of our table is correct"
        assert self.table.tablespace_name == 'USERS'

    def test_table_type(self):
        "Make sure the table_type attribute of our table is correct"
        # Postgres tables shouldn't set the table_type, its only useful for MySQL
        assert self.table.table_type == None

    def test_table_dump(self):
        "Test the dump method on the table and make sure it produces some output"
        start_string = 'Table : %s' % self.table_name
        assert self.table.dump().startswith(start_string)

    def test_col1_dump(self):
        "Is col1 properly represented in the dump output?"
        col1_re = re.compile('col1\s*numeric\s*NOT NULL\n')
        assert col1_re.search(self.table.dump()) != None

    def test_col2_dump(self):
        "Is col1 properly represented in the dump output?"
        col2_re = re.compile('col2\s*text\s*\n')
        assert col2_re.search(self.table.dump()) != None

    def test_dump_with_constraints(self):
        "Make sure that the dump method includes the table constraints"
        dump_re = re.compile('Constraints;')
        assert dump_re.search(self.table.dump()) != None

    def test_table_to_xml(self):
        "Test that the to_xml method produces some output"
        start_string = '<table name="%s">' % self.table_name
        assert self.table.to_xml().startswith(start_string)

    def test_col1_to_xml(self):
        "Ensure that col1 is properly rendere by the to_xml method"
        assert '<column name="col1" data-type="numeric" sequence="1">' in self.table.to_xml()

    def test_col2_to_xml(self):
        "Ensure that col1 is properly rendere by the to_xml method"
        assert '<column name="col2" data-type="text" sequence="2">' in self.table.to_xml()

    def test_table_compare(self):
        "Test that our equivalent tables compare as such"
        table = Table(self.table_name, self.cursor, self.schema)
        assert self.table == table

    def test_additional_columns(self):
        "Add a series of columns and after each check that _getTable still works"
        for column in ( 'varchar_col VARCHAR(255)'
            ,'char_col CHAR(255)'
            ,'integer_col INTEGER'
            ,'date_col DATE'
            ,'numeric_col NUMERIC(38,3)'
            # ,'float_col FLOAT(9,2)'
            ):
            yield self.add_column, column

    def add_column(self, column_definition):
        stmt = "ALTER TABLE %s ADD COLUMN %s" % (self.table_name, column_definition)
        log.debug(stmt)
        self.cursor.execute(stmt)
        self.db.commit()
        table = Table(self.table_name, self.cursor)

    def test_invalid_table_name(self):
        "Make sure an appopriate exception is raised if we ask for a non-existent table"
        py.test.raises(AttributeError, Table, None, self.cursor)


class TestTableFromDbConstraints(TableFromDbParent):
    "Unit tests for table constraints returned from the data dictionary"
    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor, self.schema)
        self.pk_name = '%s_pk' % self.table_name

    def test_pk_exists(self):
        "Does the table contain our primary key?"
        assert self.pk_name in self.table.constraints 

    def test_pk_name(self):
        "Does the primary key have the correct name?"
        assert self.table.constraints[self.pk_name]['name'] == self.pk_name

    def test_pk_type(self):
        "Is the primary key identified as a 'Primary' constraint"
        assert self.table.constraints[self.pk_name]['type'] == 'Primary'

    def test_pk_columns(self):
        "Does the primary key constraint refer to the correct columns?"
        assert self.table.constraints[self.pk_name]['columns'] == ['col1',]


class TestTableAndIndexFromDb(object):

    def setup_class(self):
        "Create our table and index in the designated database"
        self.table_name = 'test_tab_index_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_stmt = """CREATE TABLE %s
          ( col1 NUMERIC(16) NOT NULL 
           ,col2 VARCHAR(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.table_stmt)
        self.index_stmt = """CREATE INDEX %s_ind1 ON %s ( col2 )""" % (self.table_name, self.table_name)
        self.cursor.execute(self.index_stmt)
        self.db.commit()
        self.table = Table(self.table_name, self.cursor)

    def teardown_class(self):
        """Clean up our temporary table
        
        Dropping the table will drop the index so we don't need to do that 
        explicitly.
        """
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.commit()

    def test_round_trip(self):
        """Does the get_ddl method generate equivalent SQL to the original?
        
        This one gets tricky because the strings are never going to be exactly
        the same. 
        """
        ddl = self.table.get_ddl()
        # Do they match after white space has been removed?
        table_re = re.compile('CREATE\sTABLE\s%s' % self.table_name, re.IGNORECASE)
        assert table_re.match(ddl) != None

    def test_index_round_trip(self):
        "Does the _getIndexDDL method generate the correct SQL?"
        index_ddl = self.table.get_index_ddl()
        log.debug(index_ddl)
        index_re = re.compile('CREATE\sINDEX\s%s_ind1' % self.table_name, re.IGNORECASE)
        assert index_re.match(index_ddl) != None


class TestTableAndFkFromDb(object):
    """
    Test two tables with a foreign key defined between them.

    In this test case I'm also going to test composite primary keys which should
    be in separate unit tests but I'll split them if and when I encounter any
    errors.
    """

    def setup_class(self):
        "Create the necessary tables and constraints in the designated database"
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.schema = 'public'
        self.parent_table_name = 'test_tab_cons1_from_db'
        self.parent_table_stmt = """CREATE TABLE %s
          ( col1 NUMERIC(16) NOT NULL 
           ,col2 VARCHAR(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1)
          )
        """ % (self.parent_table_name, self.parent_table_name)
        self.cursor.execute(self.parent_table_stmt)
        self.child_table_name = 'test_tab_cons2_from_db'
        self.child_fk_name = 'parent_child_fk'
        self.child_table_stmt = """CREATE TABLE %s
          ( cola NUMERIC(16) NOT NULL
           ,colb NUMERIC(9) NOT NULL
           ,colc VARCHAR(2000) 
           ,col1 NUMERIC(16) NOT NULL
           ,CONSTRAINT %s FOREIGN KEY (col1) REFERENCES %s (col1)
           ,CONSTRAINT %s_pk PRIMARY KEY (cola, colb)
          ) 
        """ % (self.child_table_name, self.child_fk_name, self.parent_table_name, self.child_table_name, )
        self.cursor.execute(self.child_table_stmt)
        self.db.commit()

    def setup_method(self, method):
        self.child_table = Table(self.child_table_name, self.cursor, self.schema)
        self.parent_table = Table(self.parent_table_name, self.cursor, self.schema)

    def test_get_child_table_from_db(self):
        "Does the _getTable method work correctly for the child table?"
        self.child_table = Table(self.child_table_name, self.cursor, self.schema)

    def test_constraint_defined(self):
        "Have we registered the foreign key owned by the child table?"
        assert self.child_table.constraints.has_key(self.child_fk_name)

    def test_constraint_type(self):
        "Is the constraint type correct?"
        constraint_type = self.child_table.constraints[self.child_fk_name]['type']
        assert constraint_type == 'Foreign'

    def todo_test_constraint_columns(self):
        "Does the constraint contain the correct column(s)?"
        # Column names are a sequence after the constraint type
        columns = self.child_table.constraints[self.child_fk_name][1]

    def test_get_parent_table_from_db(self):
        "Does the _getTable method work correctly for the parent table?"
        self.parent_table = Table(self.parent_table_name, self.cursor)

    def test_table_and_fk_round_trip(self):
        """Does the _get_ddl method generate equivalent SQL to the original?
        
        This one gets tricky because the strings are never going to be exactly
        the same.

        We need to break our original DDL into its component parts and check 
        that they are present in the generated DDL string.

        Its also quite fragile because there is no guarantee what order the 
        columns or constraints are going to be included in the two different
        DDL strings. We should probably have some sort of tree of the key elements
        of the table and make sure that they are included in each string.
        """
        # Get the DDL from the objects we created in the last two tests
        parent_ddl = self.parent_table.get_ddl()
        child_ddl = self.child_table.get_ddl()
        parent_re = re.compile('^CREATE\sTABLE.*%s' % self.parent_table_name, re.IGNORECASE)
        child_re = re.compile('^CREATE\sTABLE.*%s' % self.child_table_name, re.IGNORECASE)
        # Do they match after white space has been removed?
        assert parent_re.match(parent_ddl) != None
        assert parent_re.match(self.parent_table_stmt) != None
        assert child_re.match(child_ddl) != None
        assert child_re.match(self.child_table_stmt) != None

    def teardown_class(self):
        "Clean up our temporary tables"
        self.db.commit()
        stmt = 'DROP TABLE %s' % self.child_table_name
        self.cursor.execute(stmt)
        stmt = 'DROP TABLE %s' % self.parent_table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.commit()


class TestViewNew(object):
    "Unit test for creating views using our View class"
    def setup_class(self):
        self.view_name = 'test_view'

    def test_empty(self):
        "Can we create an empty (in memory) view?"
        self.empty_view = View(self.view_name)

    def test_empty_view_get_ddl(self):
        "Can we get valid DDL from our empty view?"
        ddl = View(self.view_name).get_ddl()
        log.debug(ddl)
        assert ddl == "CREATE VIEW %s" % self.view_name

    def test_view_without_name(self):
        view = View('no_name')
        view.name = None
        py.test.raises(AttributeError, view.get_ddl)

    def invalid_test_add_column(self):
        "Can we add a column to our new (in memory) view?"
        column_name = "empty_column"
        column = (1, column_name, 'VARCHAR', 20, None, None, 'N')
        self.empty_view.columns.append(column)
        self.empty_view.sql = "SELECT %s FROM dummy_table" % (column_name)

    def invalid_test_one_column_get_ddl(self):
        "Is the ddl we get back for our view correct?"
        ddl = self.empty_view.get_ddl()
        log.debug(ddl)
        assert ddl == "CREATE VIEW test_view ( empty_column ) AS\n  SELECT empty_column FROM dummy_table"


class TestViewParent(object):

    def setup_class(self):
        "Create our view in the designated database"
        self.view_name = 'test_view_from_db'
        self.dummy_table_name = 'empty_table'
        self.column_name = 'col1'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.dummy_table_stmt = "CREATE table %s (%s VARCHAR(50))" % (self.dummy_table_name, \
                self.column_name)
        self.view_stmt = "CREATE VIEW %s (%s) AS SELECT %s FROM %s" % (self.view_name, \
                self.column_name, self.column_name, self.dummy_table_name)
        self.cursor.execute(self.dummy_table_stmt)
        self.db.commit()
        self.cursor.execute(self.view_stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our view"
        drop_view_stmt = 'DROP VIEW %s' % self.view_name
        drop_table_stmt = 'DROP TABLE %s' % self.dummy_table_name
        self.db.commit()
        self.cursor.execute(drop_view_stmt)
        self.cursor.execute(drop_table_stmt)
        self.cursor.close()
        self.db.commit()


class TestViewFromDb(TestViewParent):

    def test_get_view_from_db(self):
        "Does the _getView method work correctly?"
        self.db_view = View(self.view_name, self.cursor)


class TestViewAttributesFromDb(TestViewParent):

    def setup_method(self, method):
        self.db_view = View(self.view_name, self.cursor)

    def test_view_name(self):
        "Is the name attribute of our view set correctly?"
        assert self.db_view.name == self.view_name

    def test_view_sql(self):
        "Is the SQL attribute of the view set?"
        assert self.db_view.sql != None

    def test_view_triggers(self):
        "If there are triggers defined are they valid?"
        if len(self.db_view.triggers) > 0:
            for trigger_name, trigger in self.db_view.triggers.items():
                assert isinstance(trigger, schema_trigger) == True

    def test_compare_views(self):
        "Does the comparison method work correctly?"
        new_view = View(self.view_name, self.cursor)
        assert self.db_view == new_view


class TestViewColumns(TestViewParent):

    def setup_method(self, method):
        self.db_view = View(self.view_name, self.cursor)
        self.columns = self.db_view.columns

    def test_view_columns_not_null(self):
        "Does this view have one or more columns defined?"
        assert len(self.db_view.columns) > 0

    def test_view_column_seq(self):
        "Does the view column have the correct sequence value?"
        assert self.columns[self.column_name]['sequence'] == 1

    def test_view_column_name(self):
        "Does the view column have the correct sequence value?"
        assert self.columns[self.column_name]['name'] == self.column_name

    def test_view_column_type(self):
        "Does the view column have the correct sequence value?"
        assert self.columns[self.column_name]['type'] == 'varchar'

    def test_view_column_length(self):
        "Does the view column have the correct length?"
        assert self.columns[self.column_name]['length'] == 50

    def test_view_column_nullable(self):
        "Does the view column have the correct length?"
        assert self.columns[self.column_name]['nullable'] == True


class TestCalcPrecision(object):
    "Test the calc_precision static method on the Table class"

    def test_data_length_only(self):
        assert Table.calc_precision('VARCHAR', '10', None, None) == '(10)'

    def test_data_length_and_others(self):
        "If a data_length is provided the data_precision and data_scale parameters are ignored"
        assert Table.calc_precision('VARCHAR', '15', 1, 1) == '(15)'

    def test_data_precision_and_scale(self):
        assert Table.calc_precision('NUMERIC', None, 9, 2) == '(9,2)'

    def test_data_type_irrelevant_length(self):
        "If we don't provide a data type we should get an exception raised"
        py.test.raises(ValueError, Table.calc_precision, None, '20', None, None)

    def test_date_data_type(self):
        "If the column is a date data type then we should get an empty return string"
        assert Table.calc_precision('date', None, None, None) == ''

    def test_text_data_type(self):
        "Text columns don't have length of precision"
        assert Table.calc_precision('text', None, None, None) == ''

    def test_data_type_irrelevant_precision(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, None, 11, 3)

    def test_negative_length(self):
        "Providing a negative data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'varchar', -1, None, None)

    def test_zero_length(self):
        "Providing a zero data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'varchar', 0, None, None)


