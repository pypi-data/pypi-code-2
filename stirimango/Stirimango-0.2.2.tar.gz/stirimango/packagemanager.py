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
import re

import pkg_resources

from stirimango import constants
from stirimango import exceptions


class Migration(object):
    '''A single changeset to the database describing up and down diff actions.

    A :class:`migration` is keyed to its creation time (rounded to the nearest
    second) and a concise description of the migration.  Examples:

     * 2010-07-04 11:32:02 create_products_table
     * 2010-07-04 11:34:33 products_add_id_column

    The creation time provides an implicit ordering for migrations that is used
    when determining the order in which to apply migrations to the database.
    The concise description should contain ASCII alphanumeric characters
    (``a-zA-Z0-9``) and the underscore (``_``).

    Migrations are created by evaluating Python code:

    .. doctest::

       >>> m = Migration('2010-07-05T00:05:00_products_add_description_column',
       ... """
       ... DESCRIPTION = 'Add column for describing the products to customers.'
       ... FORWARD = 'ALTER TABLE products ADD COLUMN desc VARCHAR(128);'
       ... BACKWARD = 'ALTER TABLE products DROP COLUMN desc;'
       ... """);
       >>> repr(m)
       'Migration(2010-07-05T00:05:00_products_add_description_column)'
       >>> m.mid
       '2010-07-05T00:05:00_products_add_description_column'
       >>> m.description
       'products_add_description_column'
       >>> m.long_description
       'Add column for describing the products to customers.'
       >>> m.forward
       'ALTER TABLE products ADD COLUMN desc VARCHAR(128);'
       >>> m.backward
       'ALTER TABLE products DROP COLUMN desc;'
       >>> m.created
       datetime.datetime(2010, 7, 5, 0, 5)
    '''

    def __init__(self, mid, contents):
        self._mid = mid
        globs = {'__builtins__': []}
        locs = globs.copy()
        exec(contents, globs, locs)
        self._long_description = locs.get('DESCRIPTION', '')
        self._forward = locs.get('FORWARD', '')
        self._backward = locs.get('BACKWARD', '')

    def __repr__(self):
        '''The representation of a migration.
        '''
        return 'Migration(%s)' % self.mid

    @property
    def mid(self):
        '''The id of the migration.

        This is the migration's filename minus the ``.py`` extension.
        '''
        return self._mid

    @property
    def long_description(self):
        '''A long description of the migration

        This is a string (possibly multiple lines long) that describes the
        purpose of the migration.  This string should be descriptive as it will
        be shown to the systems administrators who will be running the
        migrations.
        '''
        return self._long_description

    @property
    def forward(self):
        '''The SQL necessary to migrate forward.
        '''
        return self._forward

    @property
    def backward(self):
        '''The SQL necessary to migrate backward.
        '''
        return self._backward

    @property
    def created(self):
        return datetime.datetime.strptime(self._mid[:19],
                constants.DATE_FORMAT)

    @property
    def description(self):
        return self._mid[20:]


class PackageManager(object):
    '''Track which migrations are available in a package.

    The set of migrations is a set of ``.py`` files within a Python package
    whose files follow a particular convention.  The Python files within the
    package have a filename matching the regular expression
    ``^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}_\w+.py$``.  Conceptually, this is
    the `datetime format string
    <http://docs.python.org/library/datetime.html#strftime-and-strptime-behavior>`_
    ``%Y-%m-%dT%H:%M:%S`` joined to a string of alphanumerics and underscores
    by a single underscore.
    '''

    def __init__(self, package):
        self.package_name = package
        self.package = get_module(package)
        self.provider = pkg_resources.get_provider(package)
        self.manager = pkg_resources.ResourceManager()
        self.config_values = {}
        for item in dir(self.package):
            if item.startswith('STIRIMANGO_'):
                self.config_values[item[11:]] = getattr(self.package, item)
        if self.config_values == {} and len(self.migration_list()) == 0:
            raise exceptions.InvalidPackage()

    def migration_list(self):
        '''Return a list of migration ids in sorted order.

        .. doctest::

           >>> m = PackageManager('testdata.sample')
           >>> pprint(m.migration_list())
           ['2010-07-04T00:00:00_create_products_table',
            '2010-07-05T00:05:00_products_add_description_column',
            '2010-07-05T00:05:50_no_description',
            '2010-07-06T00:00:00_products_remove_description_column']
        '''
        ret = []
        for filename in self.provider.resource_listdir('.'):
            if re.match(constants.MIGRATION_RE, filename):
                ret.append(filename[:-3])
        ret.sort()
        return ret

    def migrations(self):
        ret = []
        for migration in self.migration_list():
            get_resource_string = self.provider.get_resource_string
            contents = get_resource_string(self.manager, migration + '.py')
            ret.append(Migration(migration, contents))
        return ret

    @property
    def schema_safe(self):
        safe = self.config_values.get('SCHEMA_SAFE', False)
        try:
            return bool(safe)
        except ValueError:
            return False


def get_module(plugin):
    '''Turn a python module path into a module object.

    .. doctest::

       >>> import stirimango
       >>> stirimango == get_module('stirimango')
       True

    It also works on multi-component paths.

    .. doctest::

       >>> import os.path
       >>> os.path == get_module('os.path')
       True

    An :exc:`ImportError` is raised if the package or module does not exist.

    .. doctest::

       >>> get_module('stirimango.noexist')
       Traceback (most recent call last):
       ImportError: No module named noexist
    '''

    try:
        modules = plugin.split('.')
        mod = __import__(plugin, {}, {}, [])
        for module in modules[1:]:
            mod = getattr(mod, module)
        return mod
    except ImportError:
        raise
