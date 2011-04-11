import itertools

from svargaext.sqlamigrate import tabledump, files

def generate(missing_tables, deleted_tables, schema_changes):
    def upgrade_statements(is_downgrade):
        if not is_downgrade:
            table_create = missing_tables
            table_drop = deleted_tables
        else:
            table_create = deleted_tables
            table_drop = missing_tables

        for t in table_create:
            yield '    %s.create()\n' % (t.name)

        for t in table_drop:
            yield '    %s.drop()\n' % (t.name)

        yield '\n'

        for t in schema_changes.iterkeys():
            yield "    %(table)s = Table('%(table)s', meta, autoload=True)\n\n" % ({
                'table': t,
                })

        for t, c in schema_changes.iteritems():
            if not is_downgrade:
                cmissing = c[0]
                cdeleted = c[1]
                imissing = c[2]
                ideleted = []
            else:
                cmissing = c[1]
                cdeleted = c[0]
                imissing = []
                ideleted = c[2]

            for i in cmissing:
                yield '    %(table)s_%(column)s.create(table=%(table)s)\n' % ({
                        'table': t,
                        'column': i.name,
                        })

            for i in ideleted:
                yield '    drop_index(%s)\n' % dumper.dump_index(i)

            for i in cdeleted:
                yield '    %(table)s.columns.%(column)s.drop(table=%(table)s)\n' % ({
                        'table': t,
                        'column': i.name,
                        })

            for i in imissing:
                yield '    %s.create()\n' % dumper.dump_index(i)

    def init():
        for t in itertools.chain(missing_tables, deleted_tables):
            yield '%s\n\n' % dumper.dump_table(t)

        # Create missing columns definitions
        for t, c in schema_changes.iteritems():
            cmissing = c[0]
            imissing = c[2]

            yield '\n# Column changes for %s\n' % t

            for i in cmissing:
                yield '%s_%s = ' % (t, i.name) + dumper.dump_column(i)

                yield '\n'

    dumper = tabledump.TableDumper()

    content = files.read_template('script.py_tmpl')

    return content % (dict(init=''.join(init()),
                           upgrade=''.join(upgrade_statements(False)),
                           downgrade=''.join(upgrade_statements(True))))
