from svarga import db
from opster import command
from sqlalchemy import MetaData, exc
from migrate.versioning import schema, repository, exceptions

from svargaext.sqlamigrate import apps, codegen, files, utils

Repository = repository.Repository


@command(usage='APPNAME [-n DESCRIPTION][-v VER]')
def migrate_init(appname,
                 description=('n', None, 'repository description'),
                 version=('v', '1', 'initial repository version')):
    '''Initialize sqlalchemy-migrate database
    Also creates necessary tables in the database
    '''
    # Get application
    app = apps.get_app(appname)
    if app is None:
        app = apps.instrument(appname)

        if app is None:
            raise Exception('Application %s was not found or not under version '
                            'control' % appname)

    repository = app.get_repository_path()

    try:
        Repository.create(repository, description, repository_id=appname)
    except exceptions.PathFoundError:
        print 'Repository already exists.'
        return

    repo = Repository(repository)
    repo.create_script('Initial commit')

    try:
        schema.ControlledSchema.create(db.engine, repo, int(version))
    except exceptions.DatabaseAlreadyControlledError:
        print 'Database already controlled.'


@command(usage='APPNAME [-v VER]')
def migrate_apply(appname,
                  version=('v', '1', 'initial repository version')):
    '''Create necessary tables in the database
    '''
    app = apps.get_app(appname)
    repository = app.get_repository_path()

    try:
        repo = Repository(repository)
    except exceptions.InvalidRepositoryError:
        print 'Invalid repository'
        return 1

    try:
        schema.ControlledSchema.create(db.engine, repo, int(version))
    except exceptions.DatabaseAlreadyControlledError:
        print 'Database already controlled.'


@command(usage='APPNAME DESCRIPTION')
def migrate_script(appname,
                   description):
    '''Generate empty database migrate script'''
    app = apps.get_apps().get(appname, None)
    if app is None:
        print ('Error: application %s was not found or not under version '
               'control' % appname)
        return 1
    repository = app.get_repository_path()

    try:
        repo = Repository(repository)
    except exceptions.InvalidRepositoryError:
        print 'Error: invalid repository'
        return 1

    # Read template file
    content = files.read_template('default.py_tmpl')

    # Create migration script file
    files.create_script(repo, description, content)

@command(usage='[-r REPO]')
def syncdb(appname=('a', None, 'application name'),
           version=('v', None, 'version to upgrade to')):

    applications = apps.get_apps()

    # Get list of applications to migrate
    pending = []

    if appname is not None:
        if appname not in applications:
            print 'Application %s is not found or not under control' % appname

        pending.append(applications[appname])
    else:
        if version is not None:
            print ('Error: version parameter can only be used with the '
                   'application name')
            return 1

        map(pending.append, applications.itervalues())

    # Iterate through applications and check if it's already controlled
    for app in pending:
        repository = app.get_repository_path()

        try:
            repo = Repository(repository)
        except exceptions.InvalidRepositoryError:
            print 'Error: invalid repository %s' % repository
            return 1

        try:
            s = schema.ControlledSchema(db.engine, repository)
        except (exceptions.InvalidRepositoryError,
                exceptions.DatabaseNotControlledError,
                exc.NoSuchTableError):
            s = None

        if s is None or s.version == 0:
            print 'Upgrading application %s to latest version.' % app.app.name

            # Create tables using SQLA api
            map(lambda m: m.metadata.create_all(db.engine), app.models)

            # Force to latest version
            if s is not None:
                update = s.table.update(
                    s.table.c.repository_id == str(s.repository.id))
                s.engine.execute(update, version=int(s.repository.latest))
            else:
                ver = version
                if ver is None:
                    ver = repo.latest

                schema.ControlledSchema.create(db.engine, repository, ver)
        else:
            print 'Upgrading application %s to %s version' % (
                app.app.name, version or 'latest')

            utils.migrate(s, version=version)

    print 'Upgrade succeeded'


@command(usage='APPNAME VERSION')
def migrate_downgrade(appname, version):
    '''Downgrade database to specified revision'''
    app = apps.get_apps().get(appname, None)
    if app is None:
        print ('Error: application %s was not found or not under version '
               'control' % appname)
        return 1

    repository = app.get_repository_path()

    try:
        s = schema.ControlledSchema(db.engine, repository)
    except exceptions.InvalidRepositoryError:
        print 'Error: invalid repository'
        return
    except exc.NoSuchTableError:
        print 'Error: database is not under migrate control'
        return

    utils.migrate(s, version=version)

    print 'Success'


@command(usage='APPNAME DESCRIPTION')
def migrate_smart(appname, description):
    app = apps.get_app(appname)
    if app is None:
        print ('Error: application %s was not found or not under version '
               'control' % appname)
        return 1

    repository = app.get_repository_path()

    try:
        s = schema.ControlledSchema(db.engine, repository)
    except exceptions.InvalidRepositoryError:
        print 'Invalid repository'
        return
    except exc.NoSuchTableError:
        print 'Database is not under migrate control'
        return

    # Check if db is already at last version
    if int(s.version) != int(s.repository.latest):
        print 'Database is not at latest version. Update database and try again.'
        return

    # Create metadata from db
    meta = MetaData(db.engine, reflect=True)

    app_tables = {}
    db_tables = {}

    table_prefixes = set()

    # Grab tables from application
    for base in app.models:
        for model in base.__subclasses__():
            app_tables[model.__table__.name] = model.__table__

        # Contribute prefix
        table_prefixes.add('%s_' % base.Meta.tableprefix)

    # Grab tables from the database
    for name, table in meta.tables.iteritems():
        for prefix in table_prefixes:
            if name.startswith(prefix):
                db_tables[name] = table
                break

    # Detect missing and deleted tables
    def find_missing(source, dest):
        for name, table in source.iteritems():
            if name == s.repository.version_table:
                continue

            existing_table = dest.get(name, None)

            if existing_table is None:
                yield table

    missing_tables = set(find_missing(app_tables, db_tables))

    # TODO: Fix deleted by comparing table prefixes
    deleted_tables = set(find_missing(db_tables, app_tables))

    # Detect schema changes
    schema_changes = {}

    for name, table in app_tables.iteritems():
        mt = meta.tables.get(name, None)

        if mt is not None:
            def find_difference(source, dest):
                for item in source:
                    tc = dest.get(item.name, None)

                    if tc is None:
                        yield item

            missing_columns = list(find_difference(table.columns, mt.columns))
            deleted_columns = list(find_difference(mt.columns, table.columns))

            missing_indexes = []

            # Find any pending indexes that should be created
            for c in missing_columns:
                for j in table.indexes:
                    for rc in j.columns:
                        if rc.name == c.name:
                            missing_indexes.append(j)

            if missing_columns or deleted_columns or missing_indexes:
                schema_changes[name] = (missing_columns, deleted_columns,
                                        missing_indexes)

    # Generate revision file
    result = codegen.generate(missing_tables, deleted_tables, schema_changes)

    # Create new version (copy paste from sqlalchemy-migrate)
    files.create_script(s.repository, description, result)
