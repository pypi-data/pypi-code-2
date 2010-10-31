#!/usr/bin/python
"""
Introduction
============
  Test suite for mySQLSchema module from the gerald framework

  Note that this suite uses the py.test module 
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  We want to test two different aspects of the mySQLSchema module;
    - Reading a schema from a MySQL database 
    - Specifying a schema in the in memory structures

  There will be tests for both of these approaches and hopefully some checking 
  that the two starting points produce the same results.

  To run these tests you must have a MySQL database on the local server called 
  'gerald_test'. Additionally the database must contain a user called 'gerald'
  with the password 'gerald' that has full rights to this database.

  You can create this catalog and user by running the create_mysql_test.sql
  script in the 'scripts' directory of the distribution root.

  If this is not the case then modify the value of TEST_CONNECTION_STRING

  Tests relying on an existing schema will use the EXISTING_CONNECTION_STRING.
  Modify this to point to a database that has one or more objects.

  Note that because this script imports ElementTree from xml.etree you will need
  to be running Python 2.5 or later

  To Do;
    Read the connection strings from a configuration file that is not under
    version control.
"""
__date__ = (2009, 7, 11)
__version__ = (0, 4, 1)
__author__ = "Andy Todd <andy47@halfcooked.com>"

from decimal import Decimal
import os
import re
from xml.etree import ElementTree

from gerald import MySQLSchema
from gerald.mysql_schema import Table, View
from gerald.utilities.dburi import get_connection
from gerald.utilities.Log import get_log

import py.test
# Imported solely so that we can gain access to its exception hierarchy
import MySQLdb

LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_mysqlschema.log')
log = get_log('test_mysqlschema', LOG_FILENAME, 'INFO')
TEST_CONNECTION_STRING = 'mysql://gerald:gerald@localhost/gerald_test'
EXISTING_CONNECTION_STRING = 'mysql://portfolio:portfolio@localhost/portfolio'

class TestSchemaNew(object):
    "Unit tests for creating schemas using our Schema class"
    def setup_class(self):
        self.schema_name = 'empty test'

    def test_empty(self):
        "Can we create an empty (in memory) schema"
        empty_schema = MySQLSchema(self.schema_name)

    def test_name_attribute(self):
        "Does our schema object have a name attribute?"
        assert MySQLSchema(self.schema_name).name == self.schema_name

    def test_version_attribute(self):
        "Does our schema object have an api_version attribute?"
        assert hasattr(MySQLSchema(self.schema_name), 'api_version')


class TestSchemaAddTable(object):
    "Test the addition of objects to a new Schema"

    def setup_class(self):
        self.schema_name = 'empty test'
        self.table_name = 'test_table'
        self.empty_schema = MySQLSchema(self.schema_name)

    def test_new_table(self):
        "Add a table to our empty (in memory) schema"
        new_table = Table(self.table_name)
        new_table.table_type = 'InnoDB'
        self.empty_schema.schema[self.table_name] = new_table


class TestSchemaDatabase(object):
    "Unit test for creating schemas from an existing database"
    def setup_class(self):
        "Test connecting to the 'test' database"
        self.schema_name = 'test schema'
        self.test_schema = MySQLSchema(self.schema_name, EXISTING_CONNECTION_STRING)

    def test_invalid_connection_string(self):
        "If we try and create a schema without a valid connection string we should raise an exception"
        py.test.raises(MySQLdb.DatabaseError, MySQLSchema, 'invalid', 'mysql://error:error@error/error')

    def test_simple(self):
        "Test that the setup method actually returned something"
        assert self.test_schema is not None

    def test_dump(self):
        "Does the schema dump method return something?"
        assert self.test_schema.dump() is not None

    def test_name(self):
        "Does the schema name get correctly set?"
        assert self.test_schema.name == self.schema_name

    def test_schema_version(self):
        "Does the schema api_version attribute get set?"
        assert self.test_schema.api_version == Decimal('1.1')

    def test_get_ddl(self):
        "The get_ddl method should return more than an empty string"
        assert self.test_schema.get_ddl() is not None

    def test_to_xml(self):
        "The to_xml method should return something"
        assert self.test_schema.to_xml() is not None

    def test_compare(self):
        "Comparing a schema with itself should return True"
        duplicate_schema = MySQLSchema(self.schema_name, EXISTING_CONNECTION_STRING)
        assert self.test_schema == duplicate_schema


class TestNewTableParent(object):
    "Unit tests for creating tables using our Table class"
    def setup_class(self):
        self.table_name = 'test_table'
        self.table_type = 'InnoDB'
        self.column_name = 'empty_column'
        self.column = { 'sequence': 1 }
        self.column['name'] = self.column_name
        self.column['type'] = 'VARCHAR'
        self.column['nullable'] = False
        self.column['length'] = 20


class TestTableNew(TestNewTableParent):
    def test_empty(self):
        "Can we create an empty (in memory) table?"
        empty_table = Table(self.table_name)

    def test_table_without_name(self):
        "It shouldn't be possible to get DDL for a table with no name"
        table = Table('no_name')
        table.name = None
        py.test.raises(AttributeError, table.get_ddl)


class TestTableAttributes(TestNewTableParent):
    "Unit tests for attributes of Table objects"
    def setup_method(self, method):
        self.empty_table = Table(self.table_name)
        self.empty_table.table_type = self.table_type

    def test_table_type(self):
        "Is the table type set correctly?"
        assert self.empty_table.table_type == self.table_type

    def test_empty_get_ddl(self):
        "Can we get valid DDL from this empty table?"
        ddl = 'CREATE TABLE %s ENGINE=%s' % (self.table_name, self.table_type)
        assert self.empty_table.get_ddl() == ddl

    def test_add_column(self):
        "Can we add a column to our new (in memory) table?"
        self.empty_table.columns[self.column_name] = self.column

    def test_one_column_get_ddl(self):
        self.empty_table.columns[self.column_name] = self.column
        ddl = self.empty_table.get_ddl()
        assert ddl == "CREATE TABLE test_table (empty_column VARCHAR(20) NOT NULL) ENGINE=InnoDB"

    def test_indexes_empty(self):
        "Make sure no indexes have sneaked in"
        assert len(self.empty_table.indexes) == 0

    def test_constraints_empty(self):
        "Make sure no constraints have sneaked in"
        assert len(self.empty_table.constraints) == 0

    def test_triggers_empty(self):
        "Make sure no triggers have sneaked in"
        assert len(self.empty_table.triggers) == 0


class TestTableMethods(TestNewTableParent):
    "Unit tests for methods of Table objects"
    def setup_method(self, method):
        self.table = Table(self.table_name)
        self.table.table_type = self.table_type
        self.table.columns[self.column_name] = self.column

    def test_new_table_dump(self):
        table_dump = 'Table : %s\n' % self.table_name
        table_dump += '  %s                   ' % self.column_name
        table_dump += '%s(%s)      NOT NULL\n' % (self.column['type'],
                self.column['length'])
        assert self.table.dump() == table_dump

    def test_new_table_get_ddl(self):
        table_ddl = 'CREATE TABLE %s' % self.table_name
        table_ddl += ' (%s VARCHAR(20) NOT NULL)' % self.column_name
        table_ddl += ' ENGINE=%s' % self.table_type
        assert self.table.get_ddl() == table_ddl

    def test_new_table_to_xml(self):
        table_xml = '<table name="%s">\n  ' % self.table_name
        table_xml += '<column name="%s" data-type="%s" sequence="%s">\n    ' % (self.column_name, self.column['type'], self.column['sequence'])
        table_xml += '<length>%s</length>\n  ' % self.column['length']
        table_xml += '</column>\n</table>'
        assert self.table.to_xml() == table_xml

    def test_new_table_compare(self):
        new_table = Table(self.table_name)
        new_table.table_type = self.table_type
        new_table.columns[self.column_name] = self.column
        assert self.table == new_table


class TestTableDBParent(object):

    def setup_class(self):
        "Create our table in the designated database"
        log.debug("Setting up TestTableFromDb")
        self.table_name = 'test_table_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        stmt = """CREATE TABLE %s 
         ( integer_col INTEGER NOT NULL AUTO_INCREMENT
          ,varchar_col VARCHAR(255)
          ,char_col CHAR(255)
          ,varbinary_col VARBINARY(1000)
          ,date_col DATE
          ,datetime_col DATETIME
          ,timestamp_col TIMESTAMP
          ,numeric_col NUMERIC(65,3)
          ,decimal_col DECIMAL(12,3)
          ,float_col FLOAT(9,2)
          ,enum_col ENUM('0','1','2','3')
          ,CONSTRAINT %s_pk PRIMARY KEY (integer_col)
        )""" % (self.table_name, self.table_name)
        self.cursor.execute(stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up our temporary table"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestTableFromDb(TestTableDBParent):

    def test_get_table_from_db(self):
        "Does the _getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)


class TestTableFromDbAttributes(TestTableDBParent):

    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor)

    def test_column_name(self):
        "Is the column name attribute set correctly?"
        col_name = 'varbinary_col'
        varbinary_col = self.table.columns[col_name]
        assert varbinary_col['name'] == col_name

    def test_column_integer_type(self):
        "Is the integer column type set correctly?"
        assert self.table.columns['integer_col']['type'] == 'int'

    def test_column_varchar_type(self):
        "Is the varchar column type set correctly?"
        assert self.table.columns['varchar_col']['type'] == 'varchar'

    def test_column_char_type(self):
        "Is the char column type set correctly?"
        assert self.table.columns['char_col']['type'] == 'char'

    def test_column_varbinary_type(self):
        "Is the varbinary column type set correctly?"
        assert self.table.columns['varbinary_col']['type'] == 'varbinary'

    def test_column_date_type(self):
        "Is the date column type set correctly?"
        assert self.table.columns['date_col']['type'] == 'date'

    def test_column_datetime_type(self):
        "Is the datetime column type set correctly?"
        assert self.table.columns['datetime_col']['type'] == 'datetime'

    def test_column_timestamp_type(self):
        "Is the timestamp column type set correctly?"
        assert self.table.columns['timestamp_col']['type'] == 'timestamp'

    def test_column_numeric_type(self):
        "Is the numeric column type set correctly?"
        assert self.table.columns['numeric_col']['type'] == 'decimal'

    def test_column_decimal_type(self):
        "Is the decimal column type set correctly?"
        assert self.table.columns['decimal_col']['type'] == 'decimal'

    def test_column_float_type(self):
        "Is the float column type set correctly?"
        assert self.table.columns['float_col']['type'] == 'float'

    def test_column_float_precision(self):
        "Is the float column precision set correctly?"
        assert self.table.columns['float_col']['precision'] == 9

    def test_column_float_scale(self):
        "Is the float column precision set correctly?"
        assert self.table.columns['float_col']['scale'] == 2

    def test_column_enum_type(self):
        "Is the enum column type set correctly?"
        assert self.table.columns['enum_col']['type'] == 'enum'

    def test_column_enum_special(self):
        "The 'special' attribute of an enum column contains valid values"
        assert self.table.columns['enum_col']['special'] == "'0','1','2','3'"

    def test_data_length_type(self):
        "Make sure that the data length attribute of columns is a number"
        vc_col = self.table.columns['varchar_col']
        # Duck typing check - is column length a number?
        assert vc_col['length'] + 1 > vc_col['length']

    def test_data_precision_type(self):
        "Make sure that the data precision attribute of columns is a number"
        dec_col = self.table.columns['decimal_col']
        # Duck typing check - is scale a number?
        assert dec_col['precision'] + 1 > dec_col['precision']

    def test_data_scale_type(self):
        "Make sure that the data scale attribute of columns is a number"
        dec_col = self.table.columns['decimal_col']
        # Duck typing check - is dataScale (the sixth attribute) a number?
        assert dec_col['scale'] + 1 > dec_col['scale']

    def test_nullable_true(self):
        "Is the nullable flag set to True when it should be?"
        assert self.table.columns['date_col']['nullable'] == True

    def test_nullable_false(self):
        "Is the nullable flag set to False when it should be?"
        assert self.table.columns['integer_col']['nullable'] == False

    def test_special_true(self):
        "Is the special flag set when it should be?"
        assert self.table.columns['integer_col']['special'] == 'auto_increment'

    def test_special_false(self):
        "Is the special flag set to False when it should be?"
        assert not hasattr(self.table.columns['numeric_col'], 'special')

    def test_invalid_table_name(self):
        "Make sure an appopriate exception is raised if we ask for a non-existent table"
        py.test.raises(AttributeError, Table, None, self.cursor)

    def test_dump_table_name(self):
        "Does the dump method output include the table name?"
        assert 'Table : %s' % self.table_name in self.table.dump()

    def test_dump_column_name(self):
        "Does the dump method output include column details?"
        assert 'enum_col' in self.table.dump()

    def test_dump_not_null_column(self):
        "Do not null definitions appear in the output of dump?"
        int_col = re.compile('integer_col\s*int\s*NOT NULL auto_increment')
        assert int_col.search(self.table.dump()) != None

    def test_dump_with_constraints(self):
        "Make sure that the dump method includes the table constraints"
        assert 'Constraints;' in self.table.dump()

    def test_ddl_table_name(self):
        "Test the get_ddl method includes the table name"
        assert 'CREATE TABLE `%s`' % self.table_name in self.table.get_ddl()

    def test_ddl_column_name(self):
        assert '`enum_col` enum' in self.table.get_ddl()

    def test_ddl_not_null_column(self):
        "Do not null definitions appear in the output of get_ddl?"
        int_col = re.compile('integer_col\s*int\s*NOT NULL auto_increment')
        assert int_col.search(self.table.dump()) != None

    def test_to_xml_table(self):
        "Does the to_xml method return something?"
        assert self.table.to_xml().startswith('<table name="%s">' % self.table_name)

    def test_to_xml_decimal_col(self):
        "Does the to_xml method return a tag for col1?"
        assert '<column name="decimal_col" data-type="decimal"' in self.table.to_xml()


class TestTableFromDbConstraints(TestTableDBParent):
    "Unit tests for table constraints returned from the data dictionary"
    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor)
        # An interesting feature of MySQL is that it ignores specified names for
        # primary key constraints. If this ever changes just uncomment the line
        # at the end of this method.
        self.pk_name = 'PRIMARY' 
        # self.pk_name = '%s_pk' % self.table_name

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
        assert self.table.constraints[self.pk_name]['columns'] == ['integer_col',]


class TestTableCompare(TestTableDBParent):

    def setup_method(self, method):
        "Each test case requires a table object to have been created"
        self.table = Table(self.table_name, self.cursor)

    def test_table_equivalence(self):
        "Test that our equivalent tables are equivalent"
        table = Table(self.table_name, self.cursor)
        assert self.table == table

    def test_table_compare(self):
        "Test that comparing the same table to itself returns an empty string"
        table = Table(self.table_name, self.cursor)
        assert self.table.compare(table) == ""

    def test_different_tables_not_equivalent(self):
        "Test that different tables are not equivalent"
        table = Table(self.table_name, self.cursor)
        table.columns['extra'] = (99, 'EXTRA', 'VARCHAR2', 10, None, None, 'Y', None)
        assert self.table != table

    def test_different_tables_compare(self):
        "Make sure that comparing different tables returns the actual differences"
        table = Table(self.table_name, self.cursor)
        table.columns['extra'] = (99, 'extra', 'varchar', 10, None, None, 'Y', None)
        assert self.table.compare(table) == "DIFF: Column extra not in test_table_from_db"


class TestTableAndIndexParent(object):

    def setup_class(self):
        "Create our table and index in the designated database"
        self.table_name = 'test_tab_index_from_db'
        self.db = get_connection(TEST_CONNECTION_STRING)
        self.cursor = self.db.cursor()
        self.table_stmt = """CREATE TABLE %s
          ( col1 INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY 
           ,col2 VARCHAR(200)
          )""" % (self.table_name, )
        self.cursor.execute(self.table_stmt)
        self.index_name = '%s_ind1' % self.table_name
        self.index_stmt = """CREATE INDEX %s ON %s (col2)""" % (self.index_name, self.table_name)
        self.cursor.execute(self.index_stmt)
        self.db.commit()

    def teardown_class(self):
        "Clean up after ourselves"
        stmt = 'DROP TABLE %s' % self.table_name
        self.cursor.execute(stmt)
        self.cursor.close()


class TestTableAndIndexFromDb(TestTableAndIndexParent):

    def test_get_table_from_db(self):
        "Does the mySQLSchema.Table._getTable method work correctly?"
        self.table = Table(self.table_name, self.cursor)

    def test_get_index_from_db(self):
        "Does our index get included in the table definition?"
        self.table = Table(self.table_name, self.cursor)
        assert self.index_name in self.table.indexes.keys()


class TestTableAndIndexMethods(TestTableAndIndexParent):

    def setup_method(self, method):
        self.table = Table(self.table_name, self.cursor)

    def test_to_xml_ind1(self):
        "Does the to_xml method return a tag for our index?"
        print self.table.indexes.items()
        assert '<index name="%s"' % self.index_name in self.table.to_xml()

    def test_to_xml_roundtrip(self):
        "Make sure that the XML returned from to_xml is valid"
        xml_string = self.table.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)

    def test_dump_index_header(self):
        "Does the dump() output include the 'Indexes' header?"
        assert 'Indexes:' in self.table.dump()

    def test_dump_indexes(self):
        "Is our index included in the dump() output?"
        assert '%s, BTREE' % self.index_name in self.table.dump()

    def test_ddl_indexes(self):
        "Is our index included in the get_ddl() output?"
        assert 'INDEX %s' % self.index_name in self.table.get_ddl()


class TestCalcPrecision(object):
    "Test the calc_precision static method on the Table class"
    def test_data_length_only(self):
        assert Table.calc_precision('varchar', '10', None, None) == '(10)'

    def test_data_length_and_others(self):
        "If a data_length is provided the data_precision and data_scale parameters are ignored"
        assert Table.calc_precision('varchar', '15', 1, 1) == '(15)'

    def test_data_precision_and_scale(self):
        assert Table.calc_precision('numeric', None, 9, 2) == '(9,2)'

    def test_data_type_irrelevant_length(self):
        "If we don't provide a data type an exception should be raised"
        py.test.raises(ValueError, Table.calc_precision, None, '20', None, None)

    def test_date_data_type(self):
        "If the column is a date data type then we should get an empty return string"
        assert Table.calc_precision('date', None, None, None) == ''

    def test_data_type_irrelevant_precision(self):
        "Not providing a data type will raise an exception"
        py.test.raises(ValueError, Table.calc_precision, None, None, 11, 3)

    def test_negative_length(self):
        "Providing a negative data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'varchar', -1, None, None)

    def test_zero_length(self):
        "Providing a zero data_length should raise an exception"
        py.test.raises(ValueError, Table.calc_precision, 'varchar', 0, None, None)


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
        self.cursor = self.db.cursor()
        self.stmt = "CREATE VIEW %s (%s) AS select 'x' AS %s FROM dual" % (self.view_name, self.column_name, self.column_name)
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
        self.db_view = View(self.view_name, self.cursor)


class TestViewMethodsAttributes(TestViewParent):

    def setup_method(self, method):
        self.db_view = View(self.view_name, self.cursor)

    def test_view_name(self):
        "Is the name attribute of our view set correctly?"
        assert self.db_view.name == self.view_name

    def test_view_sql(self):
        "Is the SQL attribute of the view set?"
        assert self.db_view.sql != None

    def test_view_ddl(self):
        "Is the get_ddl method returning the correct value?"
        assert self.db_view.get_ddl() == "CREATE VIEW TEST_VIEW_FROM_DB ( COL1 ) AS\n  select 'x' AS `COL1`"

    def test_view_dump(self):
        "Do we get valid output from the dump method?"
        assert self.db_view.dump() is not None

    def test_compare_views(self):
        "Does the comparison method work correctly?"
        new_view = View(self.view_name, self.cursor)
        assert self.db_view == new_view

    def test_view_to_xml(self):
        "Does the to_xml method on the view produce some output"
        assert self.db_view.to_xml().startswith('<view name="')

    def test_view_to_xml_roundtrip(self):
        "Is the output from the to_xml method valid"
        xml_string = self.db_view.to_xml()
        xml_fragment = ElementTree.fromstring(xml_string)


