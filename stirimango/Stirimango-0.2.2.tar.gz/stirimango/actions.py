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


'''The complete stirimango codebase resides in this single package with no
submodules or subpackages.

More mature releases may support other RDBMS using subpackages.
'''


import os
import io
import sys

from stirimango import databasemanager
from stirimango import exceptions
from stirimango import packagemanager


def pack_db_diff(package_manager, database_manager):
    '''Return a dictionary keyed to migration ids.

    The value is a 2-tuple indicating presence of the migration in the package
    or database.
    '''
    database = database_manager
    packages = package_manager
    migrations = {}
    for mid in packages.migration_list():
        migrations[mid] = (True, False)
    for mid, app in database.migrations():
        package_side = migrations.get(mid, (False, False))[0]
        migrations[mid] = (package_side, True)
    return migrations


def action_init(connection, schema=None, stdout=None, stderr=None):
    '''Initialize the database/schema to have the required tables.
    '''
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    manager = databasemanager.DatabaseManager(connection)
    if schema:
        manager.schema(schema)
    manager.init()
    manager.commit()
    manager.close()


def action_list(package_name, stdout=None, stderr=None):
    '''List migrations available in a package.

    Argv should be a list containing a single string which is the package name.

    In the typical case, migrations will be listed in chronological order:

    .. doctest::

       >>> action_list('testdata.sample')
       2010-07-04T00:00:00_create_products_table
       <BLANKLINE>
           Create a table to hold products for sale.
       <BLANKLINE>
       2010-07-05T00:05:00_products_add_description_column
       <BLANKLINE>
           Add a column for describing the products to customers.
       <BLANKLINE>
       2010-07-05T00:05:50_no_description
       <BLANKLINE>
       2010-07-06T00:00:00_products_remove_description_column
       <BLANKLINE>
           Remove the `description` column in the `products` table.
       <BLANKLINE>
           The product descriptions will be stored somewhere else.

    If there are constants defined in the package that provide information to
    stirimango, but the package contains no migrations, stirimango will
    acknowledge this as well:

    .. doctest::

       >>> action_list('testdata.emptypackage')
       The package specified has no migrations.

    When the package contains no indication that it was created for stirimango,
    the list function will indicate such with a :exc:`exceptions.Usage` exception:

    .. doctest::

       >>> action_list('testdata.nonpackage') #doctest: +ELLIPSIS
       Traceback (most recent call last):
       stirimango.exceptions.InvalidPackage: The package specified is not a ...

    An :exc:`ImportError` is generated when the package does not exist:

    .. doctest::

       >>> action_list('testdata.noexist')
       Traceback (most recent call last):
       ImportError: No module named noexist
    '''
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    manager = packagemanager.PackageManager(package_name)
    migrations = manager.migrations()
    migration_strings = []
    for migration in migrations:
        sio = io.StringIO()
        print(migration.mid, end='', file=sio)
        long_desc = migration.long_description.split(os.linesep)
        while len(long_desc) and long_desc[0] == '':
            long_desc = long_desc[1:]
        while len(long_desc) and long_desc[-1] == '':
            long_desc.pop()
        if long_desc != []:
            print(file=sio)
            for line in long_desc:
                print(file=sio)
                print('    %s' % line, end='', file=sio)
        migration_strings.append(sio.getvalue())
    if migration_strings:
        print('\n\n'.join(migration_strings), file=stdout)
    else:
        print(_('The package specified has no migrations.'), file=stdout)


def action_status(package_name, connection, schema=None, stdout=None,
        stderr=None):
    '''Display the status of the database.
    '''
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    packman = packagemanager.PackageManager(package_name)
    dbman = databasemanager.DatabaseManager(connection)
    if schema and not packman.schema_safe:
        error = _('Schema specified for a non-schema-safe migrations package.')
        raise exceptions.Usage(error)
    if schema:
        dbman.schema(schema)
    if not dbman.is_initialized():
        raise exceptions.Usage(_('The database is not initialized.'))
    print(' %s' % _('Migrations Package'))
    print(' | %s' % _(' Database'))
    print(' V  V')
    mapping = {True: '\u2713', False: ' '}
    for mid, (pack, db) in sorted(pack_db_diff(packman, dbman).items()):
        print('[%s][%s]' % (mapping[pack], mapping[db]), mid)
    print('\nRollback order:')
    applied = sorted(dbman.migrations(), key=lambda x: x[1], reverse=True)
    for i, (mid, apptime) in enumerate(sorted(dbman.migrations(),
            key=lambda x: x[1], reverse=True)):
        print('{0}.'.format(i), mid)
    dbman.close()


def action_forward(package_name, connection, number=None, until=None,
        schema=None, stdout=None, stderr=None):
    '''Move the migrations forward.
    '''
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    if number is not None and until is not None:
        error = _('Specify either --number or --until, but not both.')
        raise exceptions.Usage(error)
    packman = packagemanager.PackageManager(package_name)
    dbman = databasemanager.DatabaseManager(connection)
    if schema and not packman.schema_safe:
        error = _('Schema specified for a non-schema-safe migrations package.')
        raise exceptions.Usage(error)
    if schema:
        dbman.schema(schema)
    if not dbman.is_initialized():
        raise exceptions.Usage(_('The database is not initialized.'))
    diff = pack_db_diff(packman, dbman)
    unapplied_migrations = sorted([mid for mid, (pack, db) in list(diff.items())
                                       if not db])
    if number is not None:
        unapplied_migrations = unapplied_migrations[:number]
    elif until is not None:
        if until not in unapplied_migrations:
            error = _('--until must specify an unapplied migration.')
            raise exceptions.Usage(error)
        offset = unapplied_migrations.index(until)
        unapplied_migrations = unapplied_migrations[:offset + 1]
    migrations = dict([(m.mid, m) for m in packman.migrations()])
    for mid in unapplied_migrations:
        dbman.forward(migrations[mid])
    if not len(unapplied_migrations):
        print(_('All migrations were already applied.'), file=stderr)
    dbman.commit()
    dbman.close()


def action_backward(package_name, connection, number=None, until=None,
        schema=None, stdout=None, stderr=None):
    '''Move the migrations backward.
    '''
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    if number is not None and until is not None:
        error = _('Specify either --number or --until, but not both.')
        raise exceptions.Usage(error)
    packman = packagemanager.PackageManager(package_name)
    dbman = databasemanager.DatabaseManager(connection)
    if schema and not packman.schema_safe:
        error = _('Schema specified for a non-schema-safe migrations package.')
        raise exceptions.Usage(error)
    if schema:
        dbman.schema(schema)
    if not dbman.is_initialized():
        raise exceptions.Usage(_('The database is not initialized.'))
    diff = pack_db_diff(packman, dbman)
    applied_migrations = [mid for mid, (pack, db) in list(diff.items()) if db]
    applied_migrations = [(mid, apptime) for mid, apptime in dbman.migrations()
                                         if mid in applied_migrations]
    applied_migrations.sort(key=lambda x: x[1], reverse=True)
    applied_migrations = [mid for mid, apptime in applied_migrations]
    if number is not None:
        applied_migrations = applied_migrations[:number]
    elif until is not None:
        if until not in applied_migrations:
            error = _('--until must specify an applied migration.')
            raise exceptions.Usage(error)
        offset = applied_migrations.index(until)
        applied_migrations = applied_migrations[:offset + 1]
    migrations = dict([(m.mid, m) for m in packman.migrations()])
    if set(applied_migrations) - set(migrations.keys()) != set([]):
        err = _('There are migrations in the db that are not in the package')
        raise exceptions.Usage(err)
    for mid in applied_migrations:
        dbman.backward(migrations[mid])
    if not len(applied_migrations):
        print(_('No migrations were available to rollback.'), file=stderr)
    dbman.commit()
    dbman.close()
