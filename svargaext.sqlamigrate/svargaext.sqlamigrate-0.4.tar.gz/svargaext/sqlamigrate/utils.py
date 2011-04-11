from svargaext.sqlamigrate import smhacks


def drop_index(index):
    # Drop index
    index.drop()

    # Clean it up
    for i in index.table.indexes:
        if i.name == index.name:
            index.table.indexes.remove(i)
            break


def transaction(f, *args, **kwargs):
    return f

    # Maybe, sometimes, SQLAlchemy will pass connection instead of the engine
    # and we'll have transactional support... Maybe.
    # WARNING: This code is disabled for now.
    def wrapper(conn, *args, **kwargs):
        trans = conn.begin()

        try:
            result = f(conn, *args, **kwargs)

            trans.commit()
            return result
        except:
            trans.rollback()
            raise

    wrapper.__name__ = f.__name__
    wrapper.__dict__ = f.__dict__
    wrapper.__doc__ = f.__doc__

    return wrapper


def migrate(s, version):
    smhacks.apply()

    changeset = s.changeset(version)
    for ver, change in changeset:
        if changeset.step < 0:
            print "Reverting %s..." % ver
        else:
            print "Applying %s..." % (ver+1)

        s.runchange(ver, change, changeset.step)
