# -*- coding: utf-8 -*-

"""
Instructions
============

Create a file named ``postgresql.conf`` in the same directory as this file and add in
the database configuration. Here's an example:

::

    # Database Connection
    database.plugnin = psycopg2
    database.database = XXX
    database.user = XXX
    database.password = XXX
    database.host = localhost
    database.port = 5432

You can also test sqlite. Here's an ``sqlite3.conf`` file:

::

    # Database Connection
    database.creator = sqlite3.connect
    database.mincached = 5
    database.database = :memory:

WARNING: This should be a database which doesn't contain any data you want to
keep because the tests will drop and create tables.

Then run this:

::

     python unit.py

The file will run the tests against each configuration in the current directory
(ie any file ending in ``.conf``).
"""

import os
import datetime

from bn import AttributeDict
from pipestack.app import App, pipe
from pipestack.ensure import ensure
from configconvert import parse_config, split_options

def assert_not_equal(*k):
    if not len(k)>=2:
        raise Exception('Please specify at least one item to compare')
    first = k[0]
    counter = 0
    for item in k[1:]:
        counter += 1
        if first == item:
            raise AssertionError('Item %s should be equal to the first item (%r) but it has the value %r'%(counter, first, item))

def assert_equal(*k):
    if not len(k)>=2:
        raise Exception('Please specify at least one item to compare')
    first = k[0]
    counter = 0
    for item in k[1:]:
        counter += 1
        if not first == item:
            raise AssertionError('Item %s is not equal to the first item %r, it has the value %r'%(counter, first, item))

@ensure('database')
def run(bag):
    connection = bag.database.connect()
    connection2 = bag.database.connect()
    # Within the same bag you always get back the same connection
    assert_equal(connection, connection2)

    # Let's create a table and do some tests
    cursor = connection.cursor()
    if bag.app.config.database.engine in ['postgresql', 'sqlite3']:
        cursor.execute(
            """
            DROP TABLE IF EXISTS test;
            """
        )
    else:
        raise Exception('Unsupported engine %r'%bag.app.config.database.engine)

    if bag.app.config.database.engine in ['postgresql']:
        cursor.execute(
            """
            CREATE TABLE test (
                test_id serial UNIQUE NOT NULL,
                username character varying(256) UNIQUE,
                password character varying(255),
                created TIMESTAMP,
                created_date DATE,
                a_number INTEGER
            );
            """
        )
    elif bag.app.config.database.engine in ['sqlite3']:
        cursor.execute(
            """
            CREATE TABLE test (
                test_id INTEGER PRIMARY KEY,
                username character varying(255) UNIQUE,
                password character varying(255),
                created TIMESTAMP,
                created_date DATE,
                a_number INTEGER
            );
            """
        )
    cursor.close()

    now = datetime.datetime.now()
    now_date = datetime.date(now.year, now.month, now.day)
    # Test inserts:
    uid = bag.database.insert_record(
        'test',
        dict(
            username=u'james السلام عليكم',
            password='123',
            created = now,
            created_date = now_date,
            a_number = 1,
        ),
        primary_key_column_name='test_id',
    )
    assert_equal(uid, 1)
    assert_equal(
        [{
            'username': u'james السلام عليكم', 
            'password': u'123', 
            'test_id': 1, 
            'created': now,
            'created_date': now_date,
            'a_number': 1,
        }],
        bag.database.query(
            """
            SELECT test_id, username, password, created,
            created_date, a_number FROM test;
            """
        )
    )
    # Test parameter substitution:
    rows = bag.database.query(
        """
        SELECT test_id, username, password FROM test WHERE username=%s AND password!='%%s';
        """,
        (u'james السلام عليكم',)
    )
    assert_equal(
        [{'username': u'james السلام عليكم', 'password': u'123', 'test_id': 1}],
        rows
    )
    # Test update
    bag.database.update_record(
        'test',
        'test_id',
        uid,
        dict(password='new', username='jimmyg'),
    )
    rows = bag.database.query(
        """
        SELECT test_id, username, password FROM test WHERE username=%s;
        """,
        (u'jimmyg',)
    )
    assert_equal(
        [{'username': u'jimmyg', 'password': u'new', 'test_id': 1}],
        rows
    )


if __name__ == '__main__':
    class TestApp(App):
        pipes = [
            pipe('database', 'databasepipe.service.connection:DatabasePipe'),
        ]

    config_files = []
    for filename in os.listdir(os.getcwd()):
        if filename.endswith('.conf'):
            config_files.append(filename)
    if not config_files:
        print 'ERROR: Could not find any configuration files.'
        print
        print __doc__
    else:
        for filename in config_files:
            print 'Running %r'%filename
            print '  DatabaseConnectionService'
            options = parse_config(filename)
            # Run with the connection service
            options['database.pool'] = u'False'
            app = TestApp(option=split_options(options))
            app.start_flow(
                run=run, 
            )
            # Run with the connection pool service
            if options['database.plugin'] == 'sqlite3':
                print '  Skipping DatabaseConnectionPoolService, SQLite3 is not threadsafe'
            else:
                print '  DatabaseConnectionPoolService'
                options['database.pool'] = u'True'
                app = TestApp(option=split_options(options))
                app.start_flow(
                    run=run, 
                )

