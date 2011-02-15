import sys

from svarga import db


class TableDumper(object):
    def __init__(self):
        # TODO: Fix me?
        dialect = sys.modules[db.engine.dialect.__module__]

        # SQLAlchemy 0.6 fix
        if not hasattr(dialect, 'colspecs'):
            dialect = dialect.dialect

        self.column_types = dict((v, k) for k, v
                                 in dialect.colspecs.iteritems())

    def dump_column(self, c):
        kwarg = []
        if c.key != c.name:
            kwarg.append('key')
        if c.primary_key:
            # 1 fix
            c.primary_key = True
            kwarg.append('primary_key')
        if not c.nullable:
            kwarg.append('nullable')
        if c.onupdate:
            kwarg.append('onupdate')
        if c.default and not callable(c.default):
            kwarg.append('default')
        #if c.index:
        #    kwarg.append('index')
        if c.server_default:
            kwarg.append('server_default')

        t = self.column_types.get(c.type.__class__, None)
        if t is not None:
            t = t()
        else:
            t = c.type

        return "Column(%s)" % ', '.join(
            [repr(c.name)] + [repr(t)] +
            [repr(x) for x in c.foreign_keys if x is not None] +
            [repr(x) for x in c.constraints] +
            ["%s=%s" % (k, repr(getattr(c, k))) for k in kwarg])

    def dump_index(self, index):
        return "Index('%s', %s%s)" % (
            index.name,
            ', '.join('%s.columns.%s' % (c.table.name, c.name) for c in index.columns),
            (index.unique and ', unique=True') or ''
            )

    def dump_table(self, table):
        def dump():
            yield "%(table)s = Table('%(table)s', meta,\n" % {'table':
                                                            table.name}
            for col in table.columns:
                yield "    %s,\n" % self.dump_column(col)

            yield ")"

        return ''.join(dump())
