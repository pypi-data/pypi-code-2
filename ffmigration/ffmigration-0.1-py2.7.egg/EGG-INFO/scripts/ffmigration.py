#!/home/ferran/code/ffmigration/vetest/bin/python
import sys
from optparse import OptionParser
import datetime
import MySQLdb
from MySQLdb.cursors import DictCursor
from MySQLdb import OperationalError
import os

VERSION = "0.1"

TABLE_NAME = "migration_history"

CREATE_TABLE_SQL = """
CREATE TABLE %s (
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(255) COLLATE utf8_bin NOT NULL,
  applied timestamp NOT NULL
        DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
""" % TABLE_NAME


def get_tables(cursor, schema):
    SELECT = """select * from information_schema.TABLES
            where TABLE_SCHEMA=%s order by TABLE_NAME"""
    cursor.execute(SELECT, (schema,))
    tables = []
    for table in cursor.fetchall():
        tables.append(table["TABLE_NAME"])
    return tables


def create_migration_table(cursor):
    cursor.execute(CREATE_TABLE_SQL)


CHECK_MIGRATION = "select * from %s where name=%%s" % TABLE_NAME


def check_migration_applied(cursor, migration):
    cursor.execute(CHECK_MIGRATION, (migration, ))

    return bool(cursor.fetchone())


INSERT_MIGRATION = """insert into %s (name,applied)
        values (%%s,%%s)""" % TABLE_NAME


def migration_applied(cursor, migration):
    now = datetime.datetime.now()
    cursor.execute(INSERT_MIGRATION, (migration, now))

    return bool(cursor.fetchone())


def run_sql_script(cursor, scriptname):

    migration = open(scriptname).read()

    steps = migration.split(";")
    for step in steps:
        step = step.strip()
        if step:
            print step
            cursor.execute(step)


USAGE = """usage: %%prog [options] database migrations_dir

Apply database migrations from migrations_dir to selected database.
migration_dir contains files with .sql extension, that are sorted
and applied.

The applied migrations are saved on a table named  '%s'
in the selected database""" % TABLE_NAME


def main(argv):

    parser = OptionParser(usage=USAGE, version=VERSION)
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

    if len(args) == 1:
        parser.error("No migrations dir providrd")

    if len(args) > 2:
        parser.error("Too many arguments" + str(args))

    schema = args[0]
    migrations_dir = os.path.abspath(args[1])

    conn_params = {
      "db": schema,
      "cursorclass": DictCursor,
    }
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
        print e.args[0], e.args[1]
        sys.exit(2)

    cursor = conn.cursor()

    if TABLE_NAME not in get_tables(cursor, schema):
        create_migration_table(cursor)
        conn.commit()

    for migration in sorted(os.listdir(migrations_dir)):
        migration_name = os.path.splitext(migration)[0]
        if check_migration_applied(cursor, migration_name):
            continue
        else:
            migration_file = os.path.join(migrations_dir, migration)
            print migration_name
            run_sql_script(cursor, migration_file)
            migration_applied(cursor, migration_name)
            conn.commit()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
