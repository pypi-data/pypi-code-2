#!/usr/bin/python
"""
Introduction
============
  Test suite for oracle_schema module from the gerald framework

  Note that this suite uses the py.test module to run
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  We want to test two different aspects of the oracle_schema module;
    - Reading a schema from an Oracle database 
    - Specifying a schema in the in memory structures

  There will be tests for both of these approaches and hopefully some checking 
  that the two starting points produce the same results.

  To run these tests you must have an Oracle schema called 'gerald' with a 
  password of 'gerald' in a database that you can access. Alter the global 
  variable TEST_INSTANCE to specify the connection identifier that describes 
  the database containing this schema.

  If you want to use a different schema then change TEST_CONNECTION_STRING

  Tests relying on an existing database will use the EXISTING_CONNECTION_STRING.
  Make sure that this points to a valid schema that contains one or more database
  objects.

  Because this module uses xml.etree for ElementTree you must be running Python 
  2.5 or later.

  To Do;
    Read the connection strings from a configuration file that is not under
    version control
"""
__date__ = (2010, 1, 7)
__version__ = (0, 4, 1)
__author__ = "Andy Todd <andy47@halfcooked.com>"

import os
import re
from xml.etree import ElementTree

# Used in all of the round trip tests
ws_re = re.compile('\s')

# Imported solely so that we can access the Exception hierarchy
import cx_Oracle

from gerald import OracleSchema
from gerald.oracle_schema import User, Table, CodeObject, Package, Sequence, Trigger, View, DatabaseLink
from gerald.utilities.dburi import get_connection
import py.test

from gerald.utilities.Log import get_log
LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_oracleschema.log')
log = get_log('test_oracleschema', LOG_FILENAME, 'INFO')

try:
    from local_connection_data import ORA_TEST_INSTANCE as TEST_INSTANCE
except ImportError:
    TEST_INSTANCE = ''
try:
    from local_connection_data import ORA_TEST_SCHEMA as TEST_SCHEMA
except ImportError:
    TEST_SCHEMA = 'GERALD'
# Make sure this points to an existing, valid, user in an Oracle database 
try:
    from local_connection_data import ORA_EXISTING_SCHEMA as EXISTING_SCHEMA
except ImportError:
    EXISTING_SCHEMA = 'PORTFOLIO'
# Users with DBA privilege open up an interesting new world
try:
    from local_connection_data import ORA_DBA_PASSWORD as DBA_PASSWORD
except ImportError:
    DBA_PASSWORD = 'MANAGER'
DBA_SCHEMA = 'SYSTEM'
TEST_CONNECTION_STRING = 'oracle://%s:%s' % (TEST_SCHEMA, TEST_SCHEMA)
EXISTING_CONNECTION_STRING = 'oracle://%s:%s' % (EXISTING_SCHEMA, EXISTING_SCHEMA)
DBA_CONNECTION_STRING = 'oracle://%s:%s' % (DBA_SCHEMA, DBA_PASSWORD)
if TEST_INSTANCE:
    TEST_CONNECTION_STRING += '@%s' % TEST_INSTANCE
    EXISTING_CONNECTION_STRING += '@%s' % TEST_INSTANCE
    DBA_CONNECTION_STRING += '@%s' % TEST_INSTANCE

class TestSchemaNew(object):
    "Unit test for creating schemas using our Schema class"
    def setup_class(self):
        self.schema_name = 'empty test'

    def test_empty(self):
        "Can we create an empty (in memory) schema"
        empty_schema = OracleSchema(self.schema_name)

    def test_name_attribute(self):
        "Does our schema object have a name attribute?"
        assert OracleSchema(self.schema_name).name == self.schema_name

    def test_version_attribute(self):
        "Does our schema object have an api_version attribute?"
        assert hasattr(OracleSchema(self.schema_name), 'api_version')


class TestSchemaAddTable(object):
    "Unit tests for adding a table to a new, empty Schema"
    def setup_class(self):
        self.schema_name = 'empty test'
        self.empty_schema = OracleSchema(self.schema_name)

    def test_new_table(self):
        "Add a table to our empty (in memory) schema"
        table_name = 'test_table'
        new_table = Table(table_name)
        new_table.tablespace_name = 'USERS'
        new_table.columns['col1'] = {'sequence': 1, 'name': 'col1', 
                'type': 'VARCHAR2', 'length': 20, 'nullable': False, 
                'default': "'Default value'"}
        self.empty_schema.schema[table_name] = new_table

    def test_new_table_ddl(self):
        log.debug('Empty schema with table DDL : %s' % self.empty_schema.get_ddl())
        assert self.empty_schema.get_ddl() != None

    def test_remove_table(self):
        "Remove the first table from the (in memory) schema"
        pass


class TestSchemaFromDb(object):
    "Unit tests for getting whole schema from database"
    def setup_class(self):
        self.schema_name = EXISTING_SCHEMA
        self.connection_string = EXISTING_CONNECTION_STRING

    def test_schema_from_db(self):
        "Can we read a schema from the database?"
        assert OracleSchema(self.schema_name, self.connection_string) is not None

    def test_schema_db_name_attribute(self):
        "Does our schema have the correct name?"
        assert OracleSchema(self.schema_name, self.connection_string).name == self.schema_name

    def test_schema_db_version_attribute(self):
        "Does our schema from the database have an api_version?"
        assert hasattr(OracleSchema(self.schema_name, self.connection_string), 'api_version')


class TestSchemaFromDbMethods(object):
    "Unit test on methods of retrieved schema"
    def setup_class(self):
        self.schema_name = EXISTING_SCHEMA
        self.schema = OracleSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_schema_dump(self):
        "Does the schema.dump method work on a retrieved schema?"
        assert self.schema.dump() is not None

    def test_schema_to_xml(self):
        "Does the to_xml method work on a retrieved schema?"
        assert self.schema.to_xml() is not None


class TestUserNew(object):
    "Unit test for creating users using our User class"
    def setup_class(self):
        self.user_name = 'empty test'

    def test_empty_user(self):
        "Can we create an empty (in memory) user"
        empty_schema = User(self.user_name)

    def test_name_attribute_user(self):
        "Does our schema object have a name attribute?"
        assert User(self.user_name).name == self.user_name

    def test_version_attribute_user(self):
        "Does our schema object have an api_version attribute?"
        assert hasattr(User(self.user_name), 'api_version')


class TestUserFromDb(object):
    def setup_class(self):
        self.user_name = EXISTING_SCHEMA
        self.connection_string = EXISTING_CONNECTION_STRING

    def test_user_from_db(self):
        "Can we read a user's details from the database?"
        assert User(self.user_name, self.connection_string) is not None

    def test_dba_user_from_db(self):
        "Can we read details of a DBA user with its hideous data dictionary objects?"
        assert User(DBA_SCHEMA, DBA_CONNECTION_STRING) is not None

    def test_dba_omit_from_db(self):
        "Can we get the details for a DBA user if we omit errors?"
        assert User(DBA_SCHEMA, DBA_CONNECTION_STRING, omit_error_objects=True) is not None

    def test_dual_in_user(self):
        "Does a new User contain a reference to sys.dual?"
        # This checks that we have retrieved tables
        assert 'SYS.DUAL' in User(self.user_name, self.connection_string).schema

    def test_all_objects_in_user(self):
        "Does a new User contain a reference to sys.all_objects?"
        # This checks that we have retrieved views
        assert 'SYS.ALL_OBJECTS' in User(self.user_name, self.connection_string).schema

    def test_user_has_many_schemas(self):
        "Does a User contain objects in more than 1 schema?"
        user = User(self.user_name, self.connection_string)
        # Once we have created the user count how many distinct schemas it
        # refers to
        distinct = {}
        [ distinct.setdefault(x.schema, 1) for x in user.schema.values() ]
        assert len(distinct) > 1

    def test_user_has_own_objects(self):
        "Does a new User contain a reference to it's own objects?"
        user = User(self.user_name, self.connection_string)
        assert self.user_name.upper() in [ x.schema for x in user.schema.values() ]


class TestNewTableParent(object):
    def setup_class(self):
        self.table_name = 'test_table'
        self.column_name = 'empty_column'
        self.column = {'sequence': 1, 'name': self.column_name, 'type': 'VARCHAR2', 
                  'length': 20, 'nullable': False}
        self.column_comment = "A comment on empty_column"


class TestTableNew(TestNewTableParent):
    "Unit tests for creating tables using our Table class"
    def test_empty(self):
        "Can we create an empty (in memory) table?"
        empty_table = Table(self.table_name)

    def test_empty_table_get_ddl(self):
        "Can we get valid DDL from this empty table?"
        ddl = Table(self.table_name).get_ddl() 
        assert ddl == "CREATE TABLE test_table;\n"

    def test_table_without_name(self):
        table = Table('no_name')
        table.name = None
        py.test.raises(AttributeError, table.get_ddl)


class TestTableAddColumns(TestNewTableParent):
    "Unit tests for adding columns and comments to a new table"

    def setup_method(self, method):
        self.empty_table = Table(self.table_name)

    def test_add_column(self):
        "Can we add a column to our new (in memory) table?"
        self.empty_table.columns[self.column_name] = self.column

    def test_add_table_comment(self):
        "Can we add a comment to our new (in memory) table?"
        comment = "A comment on test_table"
        self.empty_table.comments = comment
        assert self.empty_table.comments == comment

    def test_add_column_comment(self):
        "Can we add a comment to one of the columns of our new table?"
        self.empty_table.columns[self.column_name] = self.column
        self.empty_table.columns[self.column_name]['comment'] = self.column_comment
        assert self.empty_table.columns[self.column_name]['comment'] == self.column_comment


class TestTableColumnComments(TestNewTableParent):
    def setup_method(self, method):
        self.empty_table = Table(self.table_name)
        self.empty_table.columns[self.column_name] = self.column
        self.empty_table.columns[self.column_name]['comment'] = self.column_comment

    def test_column_comment_get_ddl(self):
        "Is the correct DDL returned for our new table with comments?"
        ddl = self.empty_table.get_ddl()
        assert ddl == "CREATE TABLE test_table\n ( empty_column VARCHAR2(20) NOT NULL );\nCOMMENT ON COLUMN test_table.empty_column IS 'A comment on empty_column';\n"


class TestTableMethods(TestNewTableParent):
    "Unit tests for methods of Table objects"
    def setup_method(self, method):
        self.table = Table(self.table_name)
        self.table.columns[self.column_name] = self.column

    def test_new_table_dump(self):
        table_dump = 'Table : %s\n' % self.table_name
        table_dump += '  %s                   ' % self.column_name
        table_dump += '%s(%s)     NOT NULL\n' % (self.column['type'],
                self.column['length'])
        assert self.table.dump() == table_dump

    def test_new_table_get_ddl(self):
        table_ddl = 'CREATE TABLE %s\n' % self.table_name
        table_ddl += ' ( %s ' % self.column_name
        table_ddl += '%s(%s) NOT NULL );\n' % (self.column['type'],
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
        assert ddl == "CREATE VIEW test_view"

    def test_view_without_name(self):
        view = View('no_name')
        view.name = None
        py.test.raises(AttributeError, view.get_ddl)


class TestViewParent(object):

    def setup_class(self):
        "Create our view in the designated database"
        self.view_name = 'TEST_VIEW_FROM_DB'
        self.column_name = 'COL1'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.schema = TEST_SCHEMA
        self.cursor = self.db.cursor()
        self.stmt = "CREATE VIEW %s (%s) AS SELECT 'x' %s FROM dual" % (self.view_name, self.column_name, self.column_name)
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our view"
        stmt = 'DROP VIEW %s' % self.view_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestViewFromDb(TestViewParent):

    def test_get_view_from_db(self):
        "Does the _getView method work correctly?"
        self.db_view = View(self.view_name, self.cursor, self.schema)


class TestViewMethodsAttributes(TestViewParent):

    def setup_method(self, method):
        self.db_view = View(self.view_name, self.cursor, self.schema)

    def test_view_name(self):
        "Is the name attribute of our view set correctly?"
        assert self.db_view.name == self.view_name

    def test_view_sql(self):
        "Is the SQL attribute of the view set?"
        assert self.db_view.sql != None

    def test_view_ddl(self):
        "Is the get_ddl method returning the correct value?"
        assert self.db_view.get_ddl() == "CREATE VIEW TEST_VIEW_FROM_DB ( COL1 ) AS\n  SELECT 'x' COL1 FROM dual"

    def test_view_dump(self):
        "Do we get valid output from the dump method?"
        assert self.db_view.dump() is not None

    def test_compare_views(self):
        "Does the comparison method work correctly?"
        new_view = View(self.view_name, self.cursor, self.schema)
        assert self.db_view == new_view

    def test_view_to_xml(self):
        "Does the to_xml method on the view produce some output"
        assert self.db_view.to_xml().startswith('<view name="')

    def test_view_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.db_view.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)


class TestViewColumns(TestViewParent):

    def setup_method(self, method):
        self.db_view = View(self.view_name, self.cursor, self.schema)
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
        assert self.columns[self.column_name]['type'] == 'CHAR'

    def test_view_column_length(self):
        "Does the view column have the correct length?"
        assert self.columns[self.column_name]['length'] == 1

    def test_view_column_nullable(self):
        "Does the view column have the correct length?"
        assert self.columns[self.column_name]['nullable'] == True


class TestSequenceNew(object):
    "Unit test for creating sequences using our Sequence class"
    def setup_class(self):
        self.sequence_name = 'empty_sequence'

    def test_empty(self):
        "Can we create an empty (in memory) sequence?"
        self.empty_seq = Sequence(self.sequence_name)

    def test_empty_ddl(self):
        "Our new empty sequence shouldn't have any values in its attributes"
        assert Sequence(self.sequence_name).get_ddl() == "CREATE SEQUENCE empty_sequence;\n"

    def test_spurious_attribute(self):
        "Test that adding a spurious attribute doesn't effect the get_ddl output"
        empty_seq = Sequence(self.sequence_name)
        ddl = empty_seq.get_ddl()
        empty_seq.wibble = 'wibble'
        assert ddl == empty_seq.get_ddl()

    def test_full(self):
        "Can we add attributes to our in memory sequence"
        sequence = Sequence('full_sequence')
        sequence.min_value = 10
        sequence.curr_value = 103
        sequence.max_value = 200000
        sequence.increment_by = 5
        assert sequence.get_ddl() == "CREATE SEQUENCE full_sequence START WITH 103 MINVALUE 10 MAXVALUE 200000 INCREMENT BY 5;\n"


class TestSchemaDatabase(object):
    "Unit test for creating schemas from an existing database"

    def setup_class(self):
        "Set up our test connection"
        self.schema_name = EXISTING_SCHEMA
        self.test_schema = OracleSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_invalid_connection_string(self):
        "If we try and create a schema using an invalid connection string we should get an exception"
        py.test.raises(cx_Oracle.DatabaseError, OracleSchema, 'invalid', 'oracle://scot:tigger')

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
        "The toXml method should return more than an empty string"
        assert self.test_schema.to_xml() != None

    def test_compare(self):
        "Test that equivalent schemas are indicated as such"
        duplicate_schema = OracleSchema(self.schema_name, EXISTING_CONNECTION_STRING)
        assert self.test_schema == duplicate_schema


class TestTableParent(object):

    def setup_class(self):
        "Create our table in the designated database"
        self.table_name = 'test_table_from_db'
        self.schema_name = TEST_SCHEMA
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) DEFAULT 'default' NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.stmt)
        self.db.commit()
        self.table_comment = 'A meaningful comment on our table'

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()

    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor, self.schema_name)


class TestTableFromDb(TestTableParent):

    def setup_method(self, method):
        "Create the table object we are going to test"
        self.table = Table(self.table_name, self.cursor, self.schema_name)

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

    def test_tablespace_name(self):
        "Make sure the tablespace_name attribute of our table is correct"
        assert self.table.tablespace_name == 'USERS'

    def test_table_type(self):
        "Make sure the table_type attribute of our table is correct"
        # Oracle tables shouldn't set the table_type, its only useful for MySQL
        assert self.table.table_type == None

    def test_column_default(self):
        "Is the default defined against a column picked up correctly?"
        assert self.table.columns['COL2']['default'] == "'default' "

    def test_additional_columns(self):
        "Add a series of columns and after each check that _getTable still works"
        for column in ( ('varchar_col', 'VARCHAR2(255)')
            ,('char_col', 'CHAR(255)')
            ,('integer_col', 'INTEGER')
            ,('date_col', 'DATE')
            ,('numeric_col', 'NUMERIC(38,3)')
            # ,'float_col FLOAT(9,2)'
            ,('blob_col', 'BLOB')
            ):
            yield self.add_column, column

    def add_column(self, column_definition):
        stmt = "ALTER TABLE %s ADD ( %s )" % (self.table_name, ' '.join(column_definition))
        self.cursor.execute(stmt)
        table = Table(self.table_name, self.cursor, self.schema_name)
        table_ddl = table.get_ddl()
        assert column_definition[0].lower() in table_ddl.lower()

    def test_invalid_table_name(self):
        "Make sure an appopriate exception is raised if we ask for a non-existent table"
        py.test.raises(AttributeError, Table, None, self.cursor)


class TestTableCompare(TestTableParent):

    def setup_method(self, method):
        "Create the table object we are going to test"
        self.table = Table(self.table_name, self.cursor, self.schema_name)

    def test_table_equivalence(self):
        "Test that our equivalent tables are equivalent"
        table = Table(self.table_name, self.cursor, self.schema_name)
        assert self.table == table

    def test_table_compare(self):
        "Test that comparing the same table to itself returns an empty string"
        table = Table(self.table_name, self.cursor, self.schema_name)
        assert self.table.compare(table) == ""

    def test_different_tables_not_equivalent(self):
        "Test that different tables are not equivalent"
        table = Table(self.table_name, self.cursor, self.schema_name)
        table.columns['extra'] = (99, 'EXTRA', 'VARCHAR2', 10, None, None, 'Y', None)
        assert self.table.compare(table) == 'DIFF: Column extra not in test_table_from_db'


class TestAddComments(TestTableParent):

    def test_add_comment(self):
        "Can we add a table comment direct to the database?"
        stmt = "COMMENT ON TABLE %s IS '%s'" % (self.table_name, self.table_comment)
        self.cursor.execute(stmt)

    def test_add_column_comment(self):
        "Can we add a column comment direct to the database?"
        self.column_comment = 'A meaningful comment on a column in our table'
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col1', self.column_comment)
        self.cursor.execute(stmt)

    def test_add_long_column_comment(self):
        "Can we add a long (>255 character) comment direct to the database?"
        self.long_column_comment = 'abcdefghijklmnopqrstuvwxyz1234567890' * 10
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col2', self.long_column_comment)
        self.cursor.execute(stmt)

    def test_add_short_column_comment(self):
        "Can we add a short (1 character) comment direct to the database?"
        self.short_column_comment = 'a'
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col3', self.short_column_comment)
        self.cursor.execute(stmt)


class TestTableFromDbConstraints(TestTableParent):
    "Unit tests for table constraints returned from the data dictionary"
    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor, self.schema_name)
        self.pk_name = '%s_PK' % self.table_name.upper()

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
        assert self.table.constraints[self.pk_name]['columns'] == ['COL1',]


class TestTableComments(object):
    """Test the retrieval of comments against tables and columns direct from the
    database.
    """

    def setup_class(self):
        "Create our table in the designated database"
        self.table_name = 'test_table_for_comments'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.schema_name = TEST_SCHEMA
        self.cursor = self.db.cursor()
        stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) DEFAULT 'default' NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        self.cursor.execute(stmt)
        # Table level comment
        self.table_comment = 'A meaningful comment on our table'
        stmt = "COMMENT ON TABLE %s IS '%s'" % (self.table_name, self.table_comment)
        self.cursor.execute(stmt)
        # Column comment
        self.column_comment = 'A meaningful comment on a column in our table'
        stmt = "COMMENT ON COLUMN %s.%s IS '%s'" % (self.table_name, 'col1', self.column_comment)
        self.cursor.execute(stmt)
        self.db.commit()

    def test_get_table_comment(self):
        "Does the table comment we have created get included in the round trip DDL?"
        table = Table(self.table_name, self.cursor, self.schema_name)
        ddl = table.get_ddl()
        assert ddl.find(self.table_comment) != -1

    def test_get_column_comment(self):
        "Does the column comment we have created get included in the round trip DDL?"
        table = Table(self.table_name, self.cursor, self.schema_name)
        ddl = table.get_ddl()
        assert ddl.find(self.column_comment) != -1

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestTableCompareDiff(object):

    def setup_class(self):
        "Create our table in the designated database"
        # Create the first (base) table
        self.table_name = 'test_table_from_db'
        self.schema_name = TEST_SCHEMA
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        log.debug('Creating table %s' % self.table_name)
        self.cursor.execute(self.stmt)
        # This is necessary because it is used in the test method
        self.table = Table(self.table_name, self.cursor, self.schema_name)
        # Create the table to compare to
        self.new_table_name = 'test_table_from_db2'
        new_table = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL
           ,col2 VARCHAR2(10) NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,col5 VARCHAR2(255)
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.new_table_name, self.new_table_name)
        log.debug('Creating table %s' % self.new_table_name)
        self.cursor.execute(new_table)
        self.db.commit()

    def test_different_tables_compare(self):
        "Make sure that comparing almost equivalent tables returns the actual differences"
        table = Table(self.new_table_name, self.cursor, self.schema_name)
        assert self.table.compare(table) == "DIFF: Table names: test_table_from_db and test_table_from_db2\nDIFF: Column COL5 not in test_table_from_db"

    def teardown_class(self):
        "Clean up our temporary table"
        for table_name in (self.table_name, self.new_table_name):
            stmt = 'DROP TABLE %s' % table_name
            log.debug('Dropping table %s' % table_name)
            self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestMixedCaseTableName(object):
    """Make sure that our code can cope with tables (or other objects) that have
    mixed case names
    """

    def setup_class(self):
        "Create our table in the designated database"
        # Create the first (base) table
        self.table_name = '"Mixed_Case_Table"'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.schema_name = TEST_SCHEMA
        self.stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(10) NOT NULL
           ,col3 VARCHAR2(20)
           ,col4 DATE
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name.strip('"'))
        log.debug('Creating table %s' % self.table_name)
        self.cursor.execute(self.stmt)

    def test_get_table_definition(self):
        "Make sure that we can get the details of a table with a mixed case name"
        self.table = Table(self.table_name, self.cursor, self.schema_name)

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        log.debug('Dropping table %s' % self.table_name)
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestTableAndIndexFromDb(object):

    def setup_class(self):
        "Create our table and index in the designated database"
        self.table_name = 'TEST_TAB_INDEX_FROM_DB'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.schema_name = TEST_SCHEMA
        self.cursor = self.db.cursor()
        self.table_stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.table_name, self.table_name)
        self.cursor.execute(self.table_stmt)
        self.index_name = '%s_IND1' % self.table_name
        self.index_stmt = """CREATE INDEX %s ON %s ( col2 )""" % (self.index_name, self.table_name)
        self.cursor.execute(self.index_stmt)
        self.db.commit()

    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor, self.schema_name)

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
        "Does the get_index_ddl method generate the correct SQL?"
        index_ddl = self.table._get_index_ddl()
        index_re = re.compile('CREATE\sINDEX\s%s' % self.index_name, re.IGNORECASE)
        assert index_re.match(index_ddl) != None

    def test_index_type(self):
        "Does the round trip index have the correct type?"
        assert self.table.indexes[self.index_name]['type'] == 'NORMAL'

    def test_index_uniqueness(self):
        "Is the round trip index object unique?"
        assert self.table.indexes[self.index_name]['unique'] == False

    def test_index_columns(self):
        "Does the round trip index have the right columns?"
        assert self.table.indexes[self.index_name]['columns'] == ['COL2']

    def test_index_dump(self):
        "Does the dump method output include the name of the trigger?"
        dump_output = self.table.dump()
        dump_re_index_name = re.compile(self.index_name, re.IGNORECASE)
        assert dump_re_index_name.search(dump_output) != None

    def test_table_name_dump(self):
        "Does the dump method output include the name of the table?"
        dump_output = self.table.dump()
        dump_re_table_name = re.compile(self.table_name, re.IGNORECASE)
        assert dump_re_table_name.search(dump_output) != None

    def test_to_xml_with_index(self):
        to_xml_output = self.table.to_xml()
        index_xml_re = re.compile('<index name="%s"' % self.index_name, re.IGNORECASE)
        assert index_xml_re.search(to_xml_output) != None

    def teardown_class(self):
        """Clean up our temporary table
        
        Dropping the table will drop the index so we don't need to do that 
        explicitly.
        """
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


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
        self.schema_name = TEST_SCHEMA
        self.cursor = self.db.cursor()
        self.parent_table_name = 'test_tab_cons1_from_db'
        self.parent_table_stmt = """CREATE TABLE %s
          ( col1 NUMBER(16) NOT NULL 
           ,col2 VARCHAR2(200) 
           ,CONSTRAINT %s_pk PRIMARY KEY (col1))
          TABLESPACE USERS
        """ % (self.parent_table_name, self.parent_table_name)
        self.cursor.execute(self.parent_table_stmt)
        self.child_table_name = 'test_tab_cons2_from_db'
        self.child_fk = 'PARENT_CHILD_FK'
        self.child_table_stmt = """CREATE TABLE %s
          ( cola NUMBER(16) NOT NULL
           ,colb NUMBER(9) NOT NULL
           ,colc VARCHAR2(2000) 
           ,col1 NUMBER(16) NOT NULL
           ,CONSTRAINT %s FOREIGN KEY (col1) REFERENCES %s (col1)
           ,CONSTRAINT %s_pk PRIMARY KEY (cola, colb)
          ) TABLESPACE USERS
        """ % (self.child_table_name, self.child_fk, self.parent_table_name, self.child_table_name, )
        self.cursor.execute(self.child_table_stmt)
        self.db.commit()

    def setup_method(self, method):
        self.child_table = Table(self.child_table_name, self.cursor,
                self.schema_name)
        self.parent_table = Table(self.parent_table_name, self.cursor,
                self.schema_name)

    def test_table_and_fk_round_trip(self):
        """Does the get_ddl method generate equivalent SQL to the original?
        
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

    def test_exact_parent_ddl(self):
        """Very fragile test to test (character by character) the output of get_ddl

        Ideally this should be covered by the previous test but this is an 
        interim measure until I improve my regex fu.
        """
        expected_parent_ddl = "CREATE TABLE %s\n ( COL1 NUMBER(16) NOT NULL\n  ,COL2 VARCHAR2(200) )\n TABLESPACE USERS;\nALTER TABLE %s ADD CONSTRAINT %s_PK PRIMARY KEY (COL1);\n" % (self.parent_table_name, self.parent_table_name, self.parent_table_name.upper())
        assert self.parent_table.get_ddl() == expected_parent_ddl

    def test_constraint_type(self):
        "Is the type of the constraint set correctly?"
        assert self.child_table.constraints[self.child_fk]['type'] == 'Foreign'

    def test_constraint_enabled(self):
        "Is the enabled flag of the constraint set correctly?"
        assert self.child_table.constraints[self.child_fk]['enabled'] == True

    def test_dump_with_constraints(self):
        "Make sure that the dump method includes the table constraints"
        dump_re = re.compile('Constraints;')
        assert dump_re.search(self.child_table.dump()) != None

    def teardown_class(self):
        """Clean up our temporary tables
        """
        stmt = 'DROP TABLE %s' % self.child_table_name
        self.cursor.execute(stmt)
        stmt = 'DROP TABLE %s' % self.parent_table_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestCalcPrecision(object):
    "Test the calc_precision static method on the Table class"
    def test_data_length_only(self):
        assert Table.calc_precision('VARCHAR2', '10', None, None) == '(10)'

    def test_data_length_and_others(self):
        "If a data_length is provided the data_precision and data_scale parameters are ignored"
        assert Table.calc_precision('VARCHAR2', '15', 1, 1) == '(15)'

    def test_data_precision_and_scale(self):
        assert Table.calc_precision('NUMBER', None, 9, 2) == '(9,2)'

    def test_data_precision_only(self):
        assert Table.calc_precision('NUMBER', None, 9, None) == '(9)'

    def test_data_type_irrelevant_length(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, '20', None, None)

    def test_date_data_type(self):
        "If the column is a date data type then we should get an empty return string"
        assert Table.calc_precision('DATE', None, None, None) == ''

    def test_timestamp_data_type(self):
        "If the column is a timestamp data type then we should get an empty return string"
        assert Table.calc_precision('TIMESTAMP', None, None, None) == ''

    def test_data_type_irrelevant_precision(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, None, 11, 3)

    def test_negative_length(self):
        "Providing a negative data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'VARCHAR2', -1, None, None)

    def test_zero_length(self):
        "Providing a zero data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'VARCHAR2', 0, None, None)


class TestCodeObjectNew(object):
    "Unit test for creating code objects using our CodeObject class"
    def setup_class(self):
        self.co_name = 'empty_proc'
        self.co_type = 'PROCEDURE'

    def test_empty(self):
        "Can we create an empty (in memory) code object?"
        self.empty_co = CodeObject(self.co_name, self.co_type)

    def test_no_type_fails(self):
        "Trying to create a code object without a type should fail"
        py.test.raises(TypeError, CodeObject, self.co_name)

    def test_empty_co_get_ddl(self):
        "get_ddl on our empty code object should return an empty statement"
        assert CodeObject(self.co_name, self.co_type).get_ddl() == None


class TestCodeObjectParent(object):

    def setup_class(self):
        "Create our code object(s) in the designated database"
        self.proc_name = 'test_procedure_from_db'
        self.proc_type = 'PROCEDURE'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.schema = TEST_SCHEMA
        self.cursor = self.db.cursor()
        self.stmt = """CREATE PROCEDURE %s (param1 INTEGER, param2 VARCHAR2) AS
          l_string_length NUMBER;
        BEGIN
          param1 := param1 + 1;
          l_string := len(param2);
        END;""" % self.proc_name
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our temporary code object(s)"
        stmt = 'DROP PROCEDURE %s' % self.proc_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestCodeObjectFromDb(TestCodeObjectParent):

    def test_get_co_from_db(self):
        "Does the _getCodeObject method work correctly?"
        proc = CodeObject(self.proc_name, self.proc_type, self.cursor,
                self.schema)


class TestCodeObjectMethodsAttributes(TestCodeObjectParent):

    def setup_method(self, method):
        self.proc = CodeObject(self.proc_name, self.proc_type, self.cursor, self.schema)

    def test_co_name(self):
        assert self.proc.name == self.proc_name

    def test_co_type(self):
        assert self.proc.object_type == self.proc_type

    def test_co_schema(self):
        "Does the schema attribute have a value?"
        assert self.proc.schema == self.schema

    def test_co_source_length(self):
        "Does the source of the object have more than one row defined?"
        assert len(self.proc.source) == len(self.stmt.split('\n'))

    def test_co_source_representation(self):
        "Does the source of the object consist of (line number, code) pairs?"
        assert self.proc.source[0][0] == 1

    def test_co_get_ddl(self):
        "Does the code_object get_ddl method produce output?"
        assert self.proc.get_ddl() is not None

    def test_co_dump(self):
        "Does the code_object dump method produce output?"
        assert self.proc.dump() is not None

    def test_co_to_xml_start(self):
        "Does the code_object to_xml method produce output?"
        assert self.proc.to_xml().startswith('<code_object name="')

    def test_co_to_xml_type(self):
        "Does the code_object to_xml method specify the correct type?"
        type_def = '<type value="%s" />' % self.proc_type
        xml_frag = self.proc.to_xml()
        assert type_def in xml_frag

    def test_co_to_xml_source(self):
        "Does the code_object to_xml method include source code?"
        xml_frag = self.proc.to_xml()
        assert '<source>' in xml_frag
        assert '</source>' in xml_frag

    def test_co_to_xml_end(self):
        "Does the code_object to_xml method produce output?"
        assert self.proc.to_xml().endswith('/code_object>')

    def test_co_compare(self):
        new_proc = CodeObject(self.proc_name, self.proc_type, self.cursor, self.schema)
        assert self.proc == new_proc


class TestPackageFromDb(object):

    def setup_class(self):
        "Create our code object(s) in the designated database"
        self.name = 'test_package_from_db'
        self.type = 'PACKAGE'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.schema = TEST_SCHEMA
        self.cursor = self.db.cursor()
        stmt = """CREATE PACKAGE %s AS
          FUNCTION test_func(param1 VARCHAR2) RETURN NUMBER;

          g_package_variable DATE;
        END;
        """ % self.name
        self.cursor.execute(stmt)
        stmt = """CREATE PACKAGE BODY %s AS
          FUNCTION test_func(param1 VARCHAR2) RETURN NUMBER IS
          BEGIN
            IF to_date(param1) != g_package_variable THEN
              RETURN 1;
            ELSE
              RETURN 0;
            END IF;
          END;
        END;
        """ % self.name
        self.cursor.execute(stmt)
        self.db.commit()

    def setup_method(self, method):
        # This could be in the setup_class method but no harm running it a few
        # times
        self.package = Package(self.name, self.type, self.cursor, self.schema)

    def test_package_spec(self):
        "Does the package specification start with the correct text?"
        package_spec = self.package.get_ddl()
        package_re = re.compile('^CREATE\sOR\sREPLACE\sPACKAGE.*%s' % self.name, re.IGNORECASE)
        assert package_re.match(package_spec) != None

    def test_package_body(self):
        "Does the correct package body get returned by the appropriate method?"
        package_body = self.package.get_body_ddl()
        package_body_re = re.compile('^CREATE\sOR\sREPLACE\sPACKAGE\sBODY.*%s' % self.name, re.IGNORECASE)
        assert package_body_re.match(package_body) != None

    def teardown_class(self):
        "Clean up our temporary code object(s)"
        stmt = 'DROP PACKAGE %s' % self.name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestSequence(object):
    "Abstract class providing setup and teardown methods for Sequence tests"

    def setup_class(self):
        "Create our sequence in the designated database"
        self.sequence_name = 'test_sequence_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.schema = TEST_SCHEMA
        self.cursor = self.db.cursor()
        self.stmt = 'CREATE SEQUENCE %s' % self.sequence_name
        self.cursor.execute(self.stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our sequence"
        stmt = 'DROP SEQUENCE %s' % self.sequence_name
        self.cursor.execute(stmt)
        self.cursor.close()
        self.db.close()


class TestSequenceFromDb(TestSequence):
    "Test cases for sequence returned from the database"

    def test_get_sequence_from_db(self):
        "Does the _getSequence method work correctly?"
        self.db_sequence = Sequence(self.sequence_name, self.cursor, self.schema)


class TestSequenceXml(TestSequence):

    def setup_method(self, method):
        "Note that this method is already tested in TestSequenceFromDb"
        self.db_sequence = Sequence(self.sequence_name, self.cursor, self.schema)

    def test_sequence_to_xml(self):
        "Does the to_xml method on the sequence produce some output?"
        assert self.db_sequence.to_xml().startswith('<sequence name="')

    def test_sequence_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.db_sequence.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)


class TestDatabaseLinkCreation(object):

    def setup_class(self):
        self.db_link_name = 'test_db_link'
        self.db_link_conn = 'user/password@schema'

    def test_database_link(self):
        "Can we create a new database link?"
        self.db_link = DatabaseLink(self.db_link_name)

    def test_add_connection_string(self):
        "Can we add a connection string to our new db link?"
        self.db_link = DatabaseLink(self.db_link_name)
        self.db_link.connection_string = self.db_link_conn


class TestDatabaseLink(object):

    def setup_class(self):
        self.db_link_name = 'test_db_link'
        self.db_link = DatabaseLink(self.db_link_name)
        self.db_link_conn = 'user/password@schema'
        self.db_link.connection_string = self.db_link_conn

    def test_ddl(self):
        "Does the DatabaseLink.get_ddl method return the expected results?"
        assert self.db_link.get_ddl() == "CREATE DATABASE LINK test_db_link USING 'user/password@schema'"

    def test_dump(self):
        "Does the DatabaseLink.dump method return the expected results?"
        assert self.db_link.dump() == "Database link : test_db_link\n  connection string : user/password@schema"

    def test_to_xml(self):
        "Does the DatabaseLink.to_xml method return the expected results?"
        assert self.db_link.to_xml() == '<database_link name="test_db_link">\n  <connection_string>user/password@schema</connection_string>\n</database_link>'

    def test_true_compare(self):
        "Does the DatabaseLink.compare method return the expected results?"
        other_db_link = DatabaseLink(self.db_link_name)
        other_db_link.connection_string = self.db_link_conn
        assert self.db_link.compare(other_db_link) == None

    def test_true_cmp(self):
        "Does the DatabaseLink.__cmp__ method return the expected results?"
        other_db_link = DatabaseLink(self.db_link_name)
        other_db_link.connection_string = self.db_link_conn
        assert self.db_link == other_db_link

    def test_false_compare(self):
        "Does the DatabaseLink.compare method return false when it should?"
        other_db_link = DatabaseLink(self.db_link_name)
        # Note that we aren't specifying a connection_string here
        assert self.db_link.compare(other_db_link) != None


class TestDatabaseLinkFromDb:
    pass


class TestTriggerNew(object):
    def setup_class(self):
        self.trigger_name = 'empty_trigger'
        self.scope = 'before'
        self.events = ('update', 'insert', 'delete')
        self.level = 'row'
        self.sql = """
        DECLARE
            v_empty VARCHAR2(10);
        BEGIN
            SELECT 'x'
            INTO v_empty
            FROM dual;
        END;
        """


class TestTriggerEmpty(TestTriggerNew):
    """Unit tests for creating triggers using our Trigger class
    
    This is a bit artificial as Trigger objects should only ever be created as
    part of a Table
    """
    def test_empty(self):
        "Can we create an empty in memory trigger?"
        self.empty_trigger = Trigger(self.trigger_name)

    def test_empty_ddl(self):
        "An empty trigger should produce valid DDL"
        trigger = Trigger(self.trigger_name)
        py.test.raises(ValueError, trigger.get_ddl)
    

class TestTriggerNewAttributes(TestTriggerNew):
    def test_add_attributes(self):
        "Can we populate the appropriate attributes on an empty Trigger?"
        empty = Trigger(self.trigger_name)
        empty.scope = self.scope
        empty.events = self.events
        empty.level = self.level
        empty.sql = self.sql


class Test_BIR_TriggerBase(object):
    "Parent for unit tests on before insert row level triggers"
    def setup_class(self):
        "Create table and trigger(s) in our database"
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_name = 'TEST_TRIGGER_FROM_DB'
        self.schema = TEST_SCHEMA
        self.cursor.execute('CREATE TABLE %s (column1 INTEGER NOT NULL)' % self.table_name)
        # First trigger is before insert at the row level
        self.trigger_name = 'TTFD_BEFORE_ROW_TRIG'
        self.trigger_sql = 'CREATE OR REPLACE TRIGGER %s BEFORE INSERT ON %s FOR EACH ROW ' % (self.trigger_name, self.table_name)
        self.trigger_sql += 'BEGIN null; END;'
        self.cursor.execute(self.trigger_sql)

    def teardown_class(self):
        self.cursor.execute('DROP TABLE %s' % self.table_name)
        self.cursor.close()
        self.db.close()


class Test_BIR_TriggerFromDB(Test_BIR_TriggerBase):
    "Can we get our trigger back from the database data dictionary?"
    def test_trigger1_round_trip(self):
        print "Getting details of Trigger %s from database" % self.trigger_name
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)


class Test_BIR_TriggerAttributes(Test_BIR_TriggerBase):
    """Do the various methods and attributes on our round trip Trigger act
    correctly?
    """
    def setup_method(self, method):
        "Create the Trigger object we are going to use in each unit test"
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)

    def test_trig_from_db_sql(self):
        "Do we return the same DDL we used to create the trigger?"
        assert self.trigger.sql in self.trigger_sql

    def test_trig_from_db_level(self):
        "Does our round trip trigger have the same level?"
        assert self.trigger.level == 'row'

    def test_trig_from_db_events(self):
        "Make sure the triggering events survived the round trip"
        assert self.trigger.events == ['INSERT']

    def test_trig_from_db_scope(self):
        "Is the scope on our retrieved trigger the same as our original"
        assert self.trigger.scope == 'BEFORE'

    def test_trig_from_db_name(self):
        "Does the new trigger have the right name?"
        assert self.trigger.name == self.trigger_name

    def test_trig_get_ddl(self):
        assert self.trigger_sql == self.trigger.get_ddl()

    def test_trig_dump_name(self):
        "Do the right details get included in the output of the 'dump' method?"
        dump = self.trigger.dump()
        assert self.trigger_name in dump

    def test_trig_dump_scope(self):
        dump = self.trigger.dump()
        assert self.trigger.scope in dump

    def test_trig_dump_events(self):
        dump = self.trigger.dump()
        for event in self.trigger.events:
            assert event in dump

    def test_trig_dump_level(self):
        dump = self.trigger.dump()
        assert self.trigger.level in dump

    def test_trig_dump_sql(self):
        dump = self.trigger.dump()
        assert self.trigger.sql in dump

    def test_trig_to_xml_name(self):
        "Is the name attribute of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<trigger name="%s">' % self.trigger_name in to_xml

    def test_trig_to_xml_scope(self):
        "Is the scope tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<scope>%s</scope>' % self.trigger.scope in to_xml

    def test_trig_to_xml_level(self):
        "Is the level tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<level>%s</level>' % self.trigger.level in to_xml

    def test_trig_to_xml_events(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<events>%s</events>' % self.trigger.events in to_xml

    def test_trig_to_xml_sql(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<sql>%s</sql>' % self.trigger.sql in to_xml


class Test_AUR_TriggerBase(object):
    "Parent for unit tests on before insert row level triggers"
    def setup_class(self):
        "Create table and trigger(s) in our database"
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_name = 'TEST_TRIGGER_FROM_DB'
        self.schema = TEST_SCHEMA
        self.cursor.execute('CREATE TABLE %s (column1 INTEGER NOT NULL)' % self.table_name)
        # Second trigger is after update at the row level
        self.trigger_name = 'TTFD_AFTER_ROW_TRIG'
        self.trigger_sql = 'CREATE OR REPLACE TRIGGER %s AFTER UPDATE ON %s FOR EACH ROW ' % (self.trigger_name, self.table_name)
        self.trigger_sql += 'BEGIN null; END;'
        self.cursor.execute(self.trigger_sql)

    def teardown_class(self):
        self.cursor.execute('DROP TABLE %s' % self.table_name)
        self.cursor.close()
        self.db.close()


class Test_AUR_TriggerFromDB(Test_AUR_TriggerBase):
    "Can we get our trigger back from the database data dictionary?"
    def test_trigger1_round_trip(self):
        print "Getting details of Trigger %s from database" % self.trigger_name
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)


class Test_AUR_TriggerAttributes(Test_AUR_TriggerBase):
    """Do the various methods and attributes on our round trip Trigger act
    correctly?
    """
    def setup_method(self, method):
        "Create the Trigger object we are going to use in each unit test"
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)

    def test_trig_from_db_sql(self):
        "Do we return the same DDL we used to create the trigger?"
        assert self.trigger.sql in self.trigger_sql

    def test_trig_from_db_level(self):
        "Does our round trip trigger have the same level?"
        assert self.trigger.level == 'row'

    def test_trig_from_db_events(self):
        "Make sure the triggering events survived the round trip"
        assert self.trigger.events == ['UPDATE']

    def test_trig_from_db_scope(self):
        "Is the scope on our retrieved trigger the same as our original"
        assert self.trigger.scope == 'AFTER'

    def test_trig_from_db_name(self):
        "Does the new trigger have the right name?"
        assert self.trigger.name == self.trigger_name

    def test_trig_get_ddl(self):
        assert self.trigger_sql == self.trigger.get_ddl()

    def test_trig_dump_name(self):
        "Do the right details get included in the output of the 'dump' method?"
        dump = self.trigger.dump()
        assert self.trigger_name in dump

    def test_trig_dump_scope(self):
        dump = self.trigger.dump()
        assert self.trigger.scope in dump

    def test_trig_dump_events(self):
        dump = self.trigger.dump()
        for event in self.trigger.events:
            assert event in dump

    def test_trig_dump_level(self):
        dump = self.trigger.dump()
        assert self.trigger.level in dump

    def test_trig_dump_sql(self):
        dump = self.trigger.dump()
        assert self.trigger.sql in dump

    def test_trig_to_xml_name(self):
        "Is the name attribute of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<trigger name="%s">' % self.trigger_name in to_xml

    def test_trig_to_xml_scope(self):
        "Is the scope tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<scope>%s</scope>' % self.trigger.scope in to_xml

    def test_trig_to_xml_level(self):
        "Is the level tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<level>%s</level>' % self.trigger.level in to_xml

    def test_trig_to_xml_events(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<events>%s</events>' % self.trigger.events in to_xml

    def test_trig_to_xml_sql(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<sql>%s</sql>' % self.trigger.sql in to_xml


class Test_BDS_TriggerBase(object):
    "Parent for unit tests on before delete statement level trigger"
    def setup_class(self):
        "Create table and trigger(s) in our database"
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_name = 'TEST_TRIGGER_FROM_DB'
        self.schema = TEST_SCHEMA
        self.cursor.execute('CREATE TABLE %s (column1 INTEGER NOT NULL)' % self.table_name)
        # Third trigger is before delete at the statement level
        self.trigger_name = 'TTFD_BEFORE_STMT_TRIG'
        self.trigger_sql = 'CREATE OR REPLACE TRIGGER %s BEFORE DELETE ON %s ' % (self.trigger_name, self.table_name)
        self.trigger_sql += 'BEGIN null; END;'
        self.cursor.execute(self.trigger_sql)

    def teardown_class(self):
        self.cursor.execute('DROP TABLE %s' % self.table_name)
        self.cursor.close()
        self.db.close()


class Test_BDS_TriggerFromDB(Test_BDS_TriggerBase):
    "Can we get our trigger back from the database data dictionary?"
    def test_trigger3_round_trip(self):
        print "Getting details of Trigger %s from database" % self.trigger_name
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)


class Test_BDS_TriggerAttributes(Test_BDS_TriggerBase):
    """Do the various methods and attributes on our round trip Trigger act correctly?
    """
    def setup_method(self, method):
        "Create the Trigger object we are going to use in each unit test"
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)

    def test_trig_from_db_sql(self):
        "Do we return the same DDL we used to create the trigger?"
        assert self.trigger.sql in self.trigger_sql

    def test_trig_from_db_level(self):
        "Does our round trip trigger have the same level?"
        assert self.trigger.level == 'statement'

    def test_trig_from_db_events(self):
        "Make sure the triggering events survived the round trip"
        assert self.trigger.events == ['DELETE']

    def test_trig_from_db_scope(self):
        "Is the scope on our retrieved trigger the same as our original"
        assert self.trigger.scope == 'BEFORE'

    def test_trig_from_db_name(self):
        "Does the new trigger have the right name?"
        assert self.trigger.name == self.trigger_name

    def test_trig_get_ddl(self):
        assert self.trigger_sql == self.trigger.get_ddl()

    def test_trig_dump_name(self):
        "Do the right details get included in the output of the 'dump' method?"
        dump = self.trigger.dump()
        assert self.trigger_name in dump

    def test_trig_dump_scope(self):
        dump = self.trigger.dump()
        assert self.trigger.scope in dump

    def test_trig_dump_events(self):
        dump = self.trigger.dump()
        for event in self.trigger.events:
            assert event in dump

    def test_trig_dump_level(self):
        dump = self.trigger.dump()
        assert self.trigger.level in dump

    def test_trig_dump_sql(self):
        dump = self.trigger.dump()
        assert self.trigger.sql in dump

    def test_trig_to_xml_name(self):
        "Is the name attribute of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<trigger name="%s">' % self.trigger_name in to_xml

    def test_trig_to_xml_scope(self):
        "Is the scope tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<scope>%s</scope>' % self.trigger.scope in to_xml

    def test_trig_to_xml_level(self):
        "Is the level tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<level>%s</level>' % self.trigger.level in to_xml

    def test_trig_to_xml_events(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<events>%s</events>' % self.trigger.events in to_xml

    def test_trig_to_xml_sql(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<sql>%s</sql>' % self.trigger.sql in to_xml


class Test_AUDS_TriggerBase(object):
    "Parent for unit tests on after update and delete statement level trigger"
    def setup_class(self):
        "Create table and trigger(s) in our database"
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_name = 'TEST_TRIGGER_FROM_DB'
        self.schema = TEST_SCHEMA
        self.cursor.execute('CREATE TABLE %s (column1 INTEGER NOT NULL)' % self.table_name)
        # Third trigger is before delete at the statement level
        self.trigger_name = 'TTFD_AFTER_STMT_TRIG'
        self.trigger_sql = 'CREATE OR REPLACE TRIGGER %s AFTER UPDATE OR DELETE ON %s ' % (self.trigger_name, self.table_name)
        self.trigger_sql += 'BEGIN null; END;'
        self.cursor.execute(self.trigger_sql)

    def teardown_class(self):
        self.cursor.execute('DROP TABLE %s' % self.table_name)
        self.cursor.close()
        self.db.close()


class Test_AUDS_TriggerFromDB(Test_AUDS_TriggerBase):
    "Can we get our trigger back from the database data dictionary?"
    def test_trigger4_round_trip(self):
        print "Getting details of Trigger %s from database" % self.trigger_name
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)


class Test_AUDS_TriggerAttributes(Test_AUDS_TriggerBase):
    """Do the various methods and attributes on our round trip Trigger act correctly?
    """
    def setup_method(self, method):
        "Create the Trigger object we are going to use in each unit test"
        self.trigger = Trigger(self.trigger_name, self.cursor, self.schema)

    def test_trig_from_db_sql(self):
        "Do we return the same DDL we used to create the trigger?"
        assert self.trigger.sql in self.trigger_sql

    def test_trig_from_db_level(self):
        "Does our round trip trigger have the same level?"
        assert self.trigger.level == 'statement'

    def test_trig_from_db_events(self):
        "Make sure the triggering events survived the round trip"
        assert self.trigger.events == ['UPDATE', 'DELETE']

    def test_trig_from_db_scope(self):
        "Is the scope on our retrieved trigger the same as our original"
        assert self.trigger.scope == 'AFTER'

    def test_trig_from_db_name(self):
        "Does the new trigger have the right name?"
        assert self.trigger.name == self.trigger_name

    def test_trig_get_ddl(self):
        assert self.trigger_sql == self.trigger.get_ddl()

    def test_trig_dump_name(self):
        "Do the right details get included in the output of the 'dump' method?"
        dump = self.trigger.dump()
        assert self.trigger_name in dump

    def test_trig_dump_scope(self):
        dump = self.trigger.dump()
        assert self.trigger.scope in dump

    def test_trig_dump_events(self):
        dump = self.trigger.dump()
        for event in self.trigger.events:
            assert event in dump

    def test_trig_dump_level(self):
        dump = self.trigger.dump()
        assert self.trigger.level in dump

    def test_trig_dump_sql(self):
        dump = self.trigger.dump()
        assert self.trigger.sql in dump

    def test_trig_to_xml_name(self):
        "Is the name attribute of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<trigger name="%s">' % self.trigger_name in to_xml

    def test_trig_to_xml_scope(self):
        "Is the scope tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<scope>%s</scope>' % self.trigger.scope in to_xml

    def test_trig_to_xml_level(self):
        "Is the level tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<level>%s</level>' % self.trigger.level in to_xml

    def test_trig_to_xml_events(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<events>%s</events>' % self.trigger.events in to_xml

    def test_trig_to_xml_sql(self):
        "Is the events tag of the 'to_xml' method output correct?"
        to_xml = self.trigger.to_xml()
        assert '<sql>%s</sql>' % self.trigger.sql in to_xml
