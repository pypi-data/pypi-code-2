"""\
Migration support

PipeStack provides a facility for a ``migrate`` command to ascertain whether or
not the data associated with an application is at the same version as the code
that is running. This is implemented in two parts:

* A migrate pipe which provides functions for checking installed data versions
* A migrate command which can use the migrate pipe to compare versions and can then trigger its own migrations

Wrong:

* The migrate command calls each pipe's ``migrate()`` method to actually perform the migration

Right:

* The migrate command calls the app's ``migrate()`` method to handle
  migrations. By default this just calls each pipe's ``migrate()`` method to
  actually perform the migration but you can overide it either to call
  different parts of migrations at different times or to handle migrations
  yourself.

Internally, migration information is stored in either the config file (read
only) or in the database (if ``app_from_db()`` is used).
"""

