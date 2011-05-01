import types
import logging


try:
    from django.db.models.loading import get_models
    from django.conf import settings
    from django.db import connection
    from django.core.exceptions import ObjectDoesNotExist
    DJANGO_SUPPORT = True
except ImportError:
    DJANGO_SUPPORT = False


ITEM_LIMIT = 1000  # How many items to cache before forcing an executemany.
PARAMTOKEN = '%s'
PK_ID = 'id'  # default name of primary key field
CLEAN_HOUSE = True  # To avoid crashing the django-debug-toolbar,
                    # Thanks https://bitbucket.org/ringemup :-) !!

# a mapping of different database adapters/drivers, needed to handle different
# quotations/escaping of sql fields, see the quote-method.
_DBNAME_MAP = {
    'psycopg2': 'postgres',
    'MySQLdb': 'mysql',
    'sqlite3': 'sqlite',
    'sqlite': 'sqlite',
    'pysqlite2': 'sqlite'
    }


#http://djangosnippets.org/snippets/2342/
def model_to_dict(obj, exclude_models=['AutoField', 'ForeignKey',  'OneToOneField']):
    tree = {}
    for field_name in obj._meta.get_all_field_names():
        try:
            field = getattr(obj, field_name)
        except ObjectDoesNotExist:
            continue

        if field.__class__.__name__ in ['RelatedManager', 'ManyRelatedManager']:
            if field.model.__name__ in exclude_models:
                continue

            if field.__class__.__name__ == 'ManyRelatedManager':
                exclude_models.append(obj.__class__.__name__)
            subtree = []
            for related_obj in getattr(obj, field_name).all():
                value = model_to_dict(related_obj, \
                    exclude_models=exclude_models)
                if value:
                    subtree.append(value)
            if subtree:
                tree[field_name] = subtree

            continue

        field = obj._meta.get_field_by_name(field_name)[0]
        if field.__class__.__name__ in exclude_models:
            continue

        if field.__class__.__name__ == 'RelatedObject':
            exclude_models.append(field.model.__name__)
            tree[field_name] = model_to_dict(getattr(obj, field_name), \
                exclude_models=exclude_models)
            continue

        value = getattr(obj, field_name)
        if value:
            tree[field_name] = value

    return tree


def get_defaultvalue_for_field_from_model(model, field):
    """
    Get default value, if any, for a specified field in a specified model.
    """
    if hasattr(model._meta, "_field_name_cache"):
        field_defs = model._meta._field_name_cache
    else:
        field_defs = model._meta._fields()
    for f in field_defs:
        if field == f.name:
            if type(f.default) == types.ClassType:
                if f.default.__name__ == 'NOT_PROVIDED':
                    return None
            return f.default
    return None


class DseException(Exception):
    action = 'unknown'

    def __init__(self, exception, table, sql, params):

        self.table = table
        self.sql = sql
        self.params = params
        self.exception = exception

    def __str__(self):
        return "DseException.%sError on table %s.\nSQL: %s.\nNumber of params: %s.\nException: %s" % \
               (self.action, self.table, self.sql, len(self.params), self.exception)


class InsertManyException(DseException):
    action = 'Insert'


class UpdateManyException(DseException):
    action = 'UpdateMany'


class UpdateOneException(DseException):
    action = 'UpdateOne'

    def __str__(self):
        return "DseException.%sError on table %s.\nSQL: %s.\nParams: %s.\nException: %s" % \
               (self.action, self.table, '\n'.join(self.sql), self.params, self.exception)


class DeleteManyException(DseException):
    action = 'DeleteMany'


class DSE(object):
    
    def __init__(self, model, item_limit=ITEM_LIMIT, paramtoken=PARAMTOKEN):
        self.model = model
        self.connection = connection
        self.cursor = connection.cursor()
        self.item_limit = item_limit
        self.paramtoken = paramtoken
        self.tablename = model._meta.db_table
        self.object_name = model._meta.object_name
        self.debug = False
        self.sql_calls = 0
        self.records_processed = 0

        mod = self.cursor.connection.__class__.__module__.split('.', 1)[0]
        self.dbtype = _DBNAME_MAP.get(mod)
        if self.dbtype == 'postgres':
            self._quote = lambda x: '"%s"' % x
        else:
            self._quote = lambda x: '`%s`' % x

        self.pk = model._meta.pk.name
        self.fields = self.get_fields()
        self.default_values = {}

        for key in self.fields:
            self.default_values[key] = get_defaultvalue_for_field_from_model(self.model, key)

        self.reset()

    def reset(self):
        self.item_counter = 0
        self.insert_items = []
        self.update_items = []
        self.delete_items = []
        
    def _on_add(self):
        if self.item_counter >= self.item_limit:
            self.execute_sql()

    def get_fields(self):
        default_sql = 'select * from %s LIMIT 1' % self.tablename
        sql = {
               'sqlite': default_sql,
               'mysql': default_sql,
               'postgres': default_sql
               }
        self.cursor.execute(sql.get(self.dbtype, 'select * from %s where 1=2' % self.tablename))
        self.clean_house()
        fields = []
        for idx, field_attrs in enumerate(self.cursor.description):
            fields.append(field_attrs[0])
        return fields

    def execute_sql(self):
        """
        Executes all cached sql statements, both updates and inserts.
        """
        if self.update_items:
            params_for_executemany = []
            params_for_execute = []
            # If there all fields are present we can optimize and use executemany,
            # if not we must execute each SQL call in sequence
            for items in self.update_items:
                if len(items.keys()) != len(self.fields):
                    params_for_execute.append(items)
                else:
                    found_all_fields = True
                    for field in self.fields:
                        if not field in items:
                            found_all_fields = False
                            break

                    if found_all_fields:
                        params_for_executemany.append(items)
                    else:
                        params_for_execute.append(items)

            fieldvalues = []
            for items in params_for_executemany:
                sql = ['update %s set' % self.tablename]
                m = []
                for fieldname in self.fields:
                    if fieldname == self.pk:
                        continue
                    m.append("%s = %s" % (fieldname, self.paramtoken))
                sql.append(',\n'.join(m))
                sql.append('where %s = %s' % (self.pk, self.paramtoken))
                self.records_processed += 1
                m = []
                for fieldname in self.fields:
                    if fieldname == self.pk:
                        continue
                    if fieldname in items:
                        m.append(items[fieldname])
                    else:
                        m.append(None)
                m.append(items.get(self.pk))
                fieldvalues.append(m)

                if self.debug:
                    logging.debug("Executing update: %s" % '\n'.join(sql))
                    for f in fieldvalues:
                        logging.debug(str(f))

            if fieldvalues:
                self.sql_calls += 1
                try:
                    self._execute('\n'.join(sql), fieldvalues, many=True)
                except Exception, e:
                    raise UpdateManyException(e, self.tablename, sql, fieldvalues)
                    
            for items in params_for_execute:
                sql = ['update %s set' % self.tablename]
                m = []
                fieldvalues = []
                for fieldname in items.keys():
                    if fieldname == self.pk or fieldname not in self.fields:
                        continue
                    m.append("%s = %s" % (fieldname, self.paramtoken))
                    fieldvalues.append(items[fieldname])
                sql.append(',\n'.join(m))
                sql.append('where %s = %s' % (self.pk, self.paramtoken))
                fieldvalues.append(items[self.pk])
                self.records_processed += 1
                if self.debug:
                    logging.debug("Executing update: %s" % '\n'.join(sql))
                    for f in fieldvalues:
                        logging.debug(str(f))

                self.sql_calls += 1
                try:
                    self._execute('\n'.join(sql), fieldvalues, many=False)
                except Exception, e:
                    raise UpdateOneException(e, self.tablename, sql, fieldvalues)
                    
        if self.insert_items:
            sql = 'insert into %s (%s) values (%s)' % \
                (self.tablename, ', '.join([self._quote(f) for f in self.fields if f != self.pk]), \
                  ', '.join([self.paramtoken for f in self.fields if f != self.pk]))

            fieldvalues = []
            for items in self.insert_items:
                self.records_processed += 1
                m = []
                for fieldname in self.fields:
                    if fieldname in items:
                        m.append(items[fieldname])
                    elif fieldname != self.pk:
                        m.append(None)
                fieldvalues.append(m)

            if self.debug:
                logging.debug("Executing insert: %s" % sql)
                for f in fieldvalues:
                    logging.debug(str(f))

            self.sql_calls += 1
            try:
                self._execute(sql, fieldvalues, many=True)
            except Exception, e:
                raise InsertManyException(e, self.tablename, sql, fieldvalues)            

        if self.delete_items:
            sql = "delete from %s where %s in (%s)" % \
                (self.tablename, self.pk, ','.join([str(i) for i in self.delete_items]))
            self._execute(sql, [], many=False)

        self.reset()

    def _execute(self, sql, fieldvalues, many=True):        
        try:
            if many:
                self.cursor.executemany(sql, fieldvalues)
            else:
                self.cursor.execute(sql, fieldvalues)
        except:
            self.cursor = self.connection.cursor()
            if many:
                self.cursor.executemany(sql, fieldvalues)
            else:
                self.cursor.execute(sql, fieldvalues)
        finally:
            self.clean_house()
        
    def clean_house(self):
        """
        This method removes the last query from the list of queries stored in the django connection
        object. The django-debug-toolbar modifies that list and if we leave our dse based query lying around
        it will cause the debug-toolbar to crash.

        To disable this feature set dse.CLEAN_HOUSE = False.
        This method might later on be used for other things as well.
        """
        if CLEAN_HOUSE:
            if self.debug:
                logging.debug("DSE cleaning house: removing the last query from the list of queries in the connection object.")
            if hasattr(self, 'connection'):
                if hasattr(self.connection, 'queries'):
                    self.connection.queries = self.connection.queries[:-1]

    def flush(self):
        "Clears cache, executes cached sql statements."
        self.close()

    def close(self):
        "Clears cache, executes cached sql statements."
        self.execute_sql()

    def __exit__(self, type, value, traceback):
        "Calls close when exiting the with-block."
        self.close()

    def __enter__(self):
        "When using with SomeModel.dse as d, d = self."
        return self

    def add(self, values):
        "Adds a dictionary with values to insert/update"
        # Updates:
        if values.get(self.pk, None):
            self.update_items.append(values)

        # Inserts, we check to see if there are any default values defined for this model, and add those if missing
        # Will always insert values into all columns
        else:
            final_values = {}
            if self.default_values:
                for k, v in self.default_values.items():
                    if callable(v):
                        final_values[k] = v()
                    else:
                        final_values[k] = v

            if self.pk in final_values:
                del final_values[self.pk]
            final_values.update(values)
            self.insert_items.append(final_values)
        self._on_add()

    def delete(self, pk):
        "Adds a primary key to the deletion queue."
        assert type(pk) == types.IntType, "pk argument must be integer."
        self.delete_items.append(pk)
        self._on_add()

    def execute(self, values):
        "This method will execute the sql statement. No caching."
        self.add(values)
        self.flush()

def patch_models():
    """
    This method will monkey patch all models in installed apps to expose a dse attribute.
    """
    assert hasattr(settings, 'DATABASES') or hasattr(settings, 'DATABASE'), "Database information not found in settings."
    assert len(settings.DATABASES.keys()) > 0, "No database has been configured."
    # So far we only monkey-patch models if one database has been configured.
    if len(settings.DATABASES.keys()) != 1:
        logging.warning("DSE has not monkey-patched any models because more than one database has been configured.")
        return

    for model in get_models():
        #if not model._meta.managed:
        #    continue
        setattr(model, 'dse', DSE(model, ITEM_LIMIT, PARAMTOKEN))
