# Copyright (c) 2010, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Stirimango nor the names of its contributors may be
#       used to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import datetime

from stirimango import constants
from stirimango import exceptions


class DatabaseManager(object):
    '''Track the status of migrations in the database.

    Conceptually, a database, or schema within a database, is a space that
    `stirimango` manipulates.  This object tracks what has been done (within the
    context of `stirimango`) to the database.
    '''

    def __init__(self, connection):
        self.conn = connection
        self.conn.execute('BEGIN;')
        self._schema = 'public'

    def schema(self, schema):
        '''Change the cursor to use the provided schema name.

        .. warn::

           This is *not* run as a parameterized query.  The schema name provided
           must be a valid schema name and must be from a trusted source (i.e.,
           don't allow untrusted users to control the schema name).
        '''
        rows = self.conn.prepare('''
            SELECT nspname
            FROM pg_namespace
            WHERE nspname = $1::VARCHAR''')(schema)
        if len(rows) == 0:
            raise exceptions.UnknownSchema()
        self.conn.execute('SET search_path TO %s' % schema)
        self._schema = schema

    def is_initialized(self):
        '''A boolean indicating whether the database is initialized.
        '''
        rows = self.conn.prepare('''
            SELECT tablename
            FROM pg_tables
            WHERE tablename = 'stirimango'
                AND schemaname = $1::VARCHAR''')(self._schema)
        return len(rows) > 0

    def init(self):
        '''Create the schema table in the database.

        This will raise a :exc:`stirimango.exceptions.AlreadyInitialized` in the
        event that the database has already been initialized.
        '''
        if self.is_initialized():
            raise exceptions.AlreadyInitialized()
        sql = '''
            CREATE TABLE stirimango
            (
                created TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                description VARCHAR(64) NOT NULL,
                applied TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                PRIMARY KEY (created, description)
            );
            '''
        self.conn.execute(sql)

    def commit(self):
        '''Commit the current transaction to the database.

        It will also start a new transaction for further actions.
        '''
        self.conn.execute('COMMIT;')
        self.conn.execute('BEGIN;')

    def close(self):
        '''Close the database cursor and connection.
        '''
        self.conn.close()
        self.conn.close()

    def migrations(self):
        '''Return a list of (mid, application_time) tuples.
        '''
        if not self.is_initialized():
            raise exceptions.AlreadyInitialized()
        migrations = self.conn.prepare('''
            SELECT created, description, applied
            FROM stirimango;
            ''')
        def make_mid(created, desc):
            format = constants.DATE_FORMAT
            return '%s_%s' % (created.strftime(format), desc)
        return [(make_mid(created, description), applied)
                for created, description, applied in migrations()]

    def forward(self, migration):
        self.conn.execute(migration.forward)
        self.conn.prepare('''
            INSERT INTO stirimango (created, description, applied)
            VALUES ($1, $2, $3); ''') \
            (migration.created, migration.description, datetime.datetime.now())

    def backward(self, migration):
        self.conn.execute(migration.backward)
        self.conn.prepare('''
            DELETE FROM stirimango WHERE created=$1 AND description=$2;''') \
            (migration.created, migration.description)
