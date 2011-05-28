# -*- coding: utf-8 -*-
"""
Autumn ORM
==========

.. warning::

    This module does **not** work because Autumn seems to stick to the global
    connection object and not allow us to bind it to the application object.
    For example, when we try creating a model, everything breaks if the
    *global* connection is undefined.

Support for Autumn_, a lightweight Python ORM.

    Autumn exists as a super-lightweight Object-relational mapper (ORM) for
    Python. It’s an alternative to (not a replacement of) SQLObject,
    SQLAlchemy, Storm, etc. Perhaps the biggest difference is the automatic
    population of fields as attributes.

.. _Autumn: http://autumn-orm.org/

API reference
-------------
"""
from autumn.db.connection import Database
from autumn.db.query import Query
from tool.plugins import BasePlugin


class Autumn(BasePlugin):
    """Adds the ORM feature.

    Required configuration options:

    :param db_type: database type: either ``mysql`` or ``sqlite``.

    Depending on the database type, certain positional (`db_args`) and/or
    keyword arguments (`db_kwargs`) are also required. They are passed directly
    to the database driver, i.e. `sqlite3.connect` or `MySQLdb.connect`.

    Example configuration (YAML)::

        tool.ext.autumn_orm.Autumn:
            db_type: sqlite
            db_args: [test.db]

    In order to use `Autumn` with database connection configured via standard
    Tool configuration method, you can either access the :meth:`connection` or
    use the :meth:`query` method. Here are two equally acceptable approaches::

        from tool import app

        orm = app.get_feature('orm')

        # shortcut
        items = orm.query(Item, price=123)

        # Autumn API (note the orm.connection!)
        Query(conditions={'price: 123}, model=Item, db=orm.connection)

    .. warning::

        You should never use methods such as `Model.get` because they imply
        global connection which is not supported by this extension. Always pass
        the actual connection object where possible.

    """
    features = 'orm'

    def make_env(self, db_type, db_args=None, db_kwargs=None):
        db_args = db_args or []
        db_kwargs = db_kwargs or {}
        db = Database()
        db.connect(db_type, *db_args, **db_kwargs)
        return {'connection': db}

    @property
    def connection(self):
        """Database connection, as configured here by
        :class:`tool.application.Application`.
        """
        try:
            return self.env['connection']
        except KeyError:
            raise RuntimeError('Connection to DB is missing.')

    def query(self, model, **conditions):
        """Returns a :class:`autumn.query.Query` instance with current
        connection. See official documentation for details.
        """
        return Query(conditions=conditions, model=model, db=self.connection)
