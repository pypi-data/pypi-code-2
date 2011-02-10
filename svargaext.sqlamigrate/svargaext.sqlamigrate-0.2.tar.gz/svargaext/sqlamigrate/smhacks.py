# Various sqlalchemy-migrate hacks. Like connection sharing, sqlite fixes, etc
# Hopefully they will go away very soon

def apply():
    # SQLiteColumnGenerator fix. We don't care about FK's in SQLite
    from migrate.changeset.databases.sqlite import SQLiteColumnGenerator

    def sqlite_fk_fix(original):
        def add_foreignkey(self, column):
            pass

        return add_foreignkey

    SQLiteColumnGenerator.add_foreignkey = sqlite_fk_fix(SQLiteColumnGenerator.add_foreignkey)
