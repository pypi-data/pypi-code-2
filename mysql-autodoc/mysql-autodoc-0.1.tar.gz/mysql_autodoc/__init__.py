#!/usr/bin/env python
import sys
import os
from optparse import OptionParser

import MySQLdb
from MySQLdb.cursors import DictCursor
from MySQLdb import OperationalError
from jinja2 import Environment, FileSystemLoader


VERSION = "0.1"

TEMPLATE = "db.tmpl"

def get_tables(cursor, schema):
    SELECT = "select * from TABLES where TABLE_SCHEMA=%s order by TABLE_NAME"
    cursor.execute(SELECT, (schema,))
    tables = []
    for table in cursor.fetchall():
        tables.append(table)
    return tables


def get_indexes(cursor, schema, table):
    SELECT = "show index from %s.%s" % (schema, table)
    cursor.execute(SELECT)
    indexes = []
    for row in cursor.fetchall():
        indexes.append(row)
    return indexes


def get_f_key(cursor, schema, table, column):
    SELECT = """select * from KEY_COLUMN_USAGE where TABLE_SCHEMA=%s
              and TABLE_NAME=%s
              and COLUMN_NAME=%s and REFERENCED_TABLE_NAME is not null"""
    cursor.execute(SELECT, (schema, table, column))
    fkeys = []
    for fkey in cursor.fetchall():
        fkeys.append(fkey)
    return fkeys


def get_references(cursor, schema, table):
    SELECT = """select * from KEY_COLUMN_USAGE where TABLE_SCHEMA=%s
             and REFERENCED_TABLE_NAME=%s
             order by REFERENCED_TABLE_NAME"""
    cursor.execute(SELECT, (schema, table))
    fkeys = []
    for fkey in cursor.fetchall():
        fkeys.append(fkey)
    return fkeys

USAGE = "usage: %prog [options] database"


def main(argv):

    parser = OptionParser(usage=USAGE, version=VERSION)
    parser.add_option("-f", "--file", dest="filename",
                  help="write documentation to FILE, default database.html",
                  metavar="FILE")
    parser.add_option("-H", "--host",
                  action="store", dest="host",
                  help="Database server hostname")
    parser.add_option("-u", "--user",
                  action="store", dest="user",
                  help="database username")
    parser.add_option("-p",
                  action="store_true", dest="ask_pass",
                  help="ask for a database password")
    parser.add_option("--password",
                  action="store", dest="password",
                  help="database password")
    parser.add_option("-P", "--port",
                  action="store", dest="port",
                  help="database connection port")

    options, args = parser.parse_args(argv)

    if len(args) == 0:
        parser.error("No database provided")

    if len(args) > 1:
        parser.error("Too many arguments")

    conn_params = {
      "db": "information_schema",
      "cursorclass": DictCursor,
    }

    schema = args[0]

    if options.host:
        conn_params['host'] = options.host
    if options.user:
        conn_params['user'] = options.user
    if options.ask_pass:
        import getpass
        password = getpass.getpass("%s database password : " % schema)
        conn_params['passwd'] = password
    if options.password:
        conn_params['passwd'] = options.password
    if options.port:
        conn_params['port'] = options.port

    try:
        conn = MySQLdb.connect(**conn_params)
    except OperationalError, e:
        print e.args[0] , e.args[1]
        sys.exit(2)
    cursor = conn.cursor()

    if options.filename:
        filename = options.filename
    else:
        filename = args[0] + ".html"

    tables = []
    for row in get_tables(cursor, schema):
        row = row.copy()
        # search fields
        SELECT = "select * from COLUMNS where TABLE_SCHEMA=%s and " + \
                 "TABLE_NAME=%s order by ORDINAL_POSITION"
        cursor.execute(SELECT, (row['TABLE_SCHEMA'], row['TABLE_NAME']))
        table = row['TABLE_NAME']
        fields = []
        for field in cursor.fetchall():
            field = field.copy()
            if field['IS_NULLABLE'] == 'NO':
                desc = "NOT NULL"

            field['description'] = desc
            field['f_keys'] = get_f_key(cursor, schema,
                                         table, field['COLUMN_NAME'])
            fields.append(field.copy())

        row['fields'] = fields
        row['indexes'] = get_indexes(cursor, schema, table)
        row['references'] = get_references(cursor, schema, table)
        tables.append(row)

    env = Environment(loader=FileSystemLoader(os.path.dirname(__file__)))
    template = env.get_template(TEMPLATE)

    context = {
      'tables': tables,
      'schema': schema,
    }

    page = template.render(**context)

    f = open(filename, 'w')
    f.write(page)

if __name__ == '__main__':
    sys.exit(main() or 0)
