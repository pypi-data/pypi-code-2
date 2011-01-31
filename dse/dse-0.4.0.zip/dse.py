import logging

class TableObject(object):

    def __init__(self, tablename, fields, pk = 'id'):
        self.tablename = tablename
        self.fields = fields
        self.pk = pk
        self.update_items = []
        self.insert_items = []

    def reset(self):
        self.update_items = []
        self.insert_items = []

    def add(self, values):
        if values.get(self.pk, None) != None:
            self.update_items.append(values)
        else:
            if values.has_key(self.pk) and not values.get(self.pk):
                del values[self.pk]
            self.insert_items.append(values)

    @property
    def Count(self):
        return len(self.update_items) + len(self.insert_items)

class ObjectNotRegistered(Exception): pass

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

class DelayedSqlExecutor(object):

    def __init__(self, cursor, item_limit = 1000, paramtoken = '%s'):
        self.cursor = cursor
        self.item_limit = item_limit
        self.paramtoken = paramtoken
        self.registered_objects = {}
        self.debug_mode = False
        self.sql_calls = 0
        self.records_processed = 0

    def add_object(self, tablename, pk = 'id', keyname = None):
        if not keyname:
            keyname = tablename
        self.cursor.execute('select * from %s' % tablename)
        fields = []
        for idx, field_attrs in enumerate(self.cursor.description):
            fields.append(field_attrs[0])

        if self.debug_mode:
            logging.debug("AddObject: %s. Fields = %s" % (tablename, fields))

        self.registered_objects[keyname] = TableObject(tablename, fields, pk)
    
    @property
    def TotalItemCount(self):
        total_items = 0
        for k,v in self.registered_objects.items():
            total_items += v.Count
        return total_items

    def add_item(self, tablename, values):
        to = self.registered_objects.get(tablename, None)
        if not to:
            raise ObjectNotRegistered(tablename)
        
        if self.TotalItemCount >= self.item_limit:
            self.execute_sql()

        to.add(values)

    def execute_sql(self):
        for k,v in self.registered_objects.items():
            tablename = self.registered_objects[k].tablename
            if v.update_items:
                params_for_executemany = []
                params_for_execute = []
                # If there all fields are present we can optimize and use executemany,
                # if not we must execute each SQL call in sequence
                for items in v.update_items:
                    if len(items.keys()) != len(v.fields):
                        params_for_execute.append(items)
                    else:
                        found_all_fields = True
                        for field in v.fields:
                            if not items.has_key(field):
                                found_all_fields = False
                                break

                        if found_all_fields:
                            params_for_executemany.append(items)
                        else:
                            params_for_execute.append(items)

                fieldvalues = []
                for items in params_for_executemany:
                    sql = ['update %s set' % tablename]
                    m = []
                    for fieldname in v.fields:
                        if fieldname == v.pk:
                            continue
                        m.append("%s = %s" % (fieldname, self.paramtoken))
                    sql.append(',\n'.join(m))
                    sql.append('where %s = %s' % (v.pk, self.paramtoken))
                    self.records_processed += 1
                    m = []
                    for fieldname in v.fields:
                        if fieldname == v.pk:
                            continue
                        if items.has_key(fieldname):
                            m.append(items[fieldname])
                        else:
                            m.append(None)
                    m.append(items.get(v.pk))
                    fieldvalues.append(m)

                    if self.debug_mode:
                        logging.debug("Executing update: %s" % '\n'.join(sql))
                        for f in fieldvalues:
                            logging.debug(str(f))

                if fieldvalues:                            
                    self.sql_calls += 1
                    try:
                        self.cursor.executemany('\n'.join(sql), fieldvalues)
                    except Exception, e:
                        raise UpdateManyException(e, tablename, sql, fieldvalues)

                for items in params_for_execute:
                    sql = ['update %s set' % tablename]
                    m = []
                    fieldvalues = []
                    for fieldname in items.keys():
                        if fieldname == v.pk or fieldname not in v.fields:
                            continue
                        m.append("%s = %s" % (fieldname, self.paramtoken))
                        fieldvalues.append(items[fieldname])
                    sql.append(',\n'.join(m))
                    sql.append('where %s = %s' % (v.pk, self.paramtoken))
                    fieldvalues.append(items[v.pk])
                    self.records_processed += 1
                    if self.debug_mode:
                        logging.debug("Executing update: %s" % '\n'.join(sql))
                        for f in fieldvalues:
                            logging.debug(str(f))
                            
                    self.sql_calls += 1
                    try:
                        self.cursor.execute('\n'.join(sql), fieldvalues)
                    except Exception, e:
                        raise UpdateOneException(e, tablename, sql, fieldvalues)                        

            if v.insert_items:
                fieldnames = []                
                sql = 'insert into %s (%s) values (%s)' % \
                      (v.tablename, ', '.join([f for f in v.fields if f != v.pk]), ', '.join([self.paramtoken for f in v.fields if f != v.pk]))
                fieldvalues = []
                for items in v.insert_items:
                    self.records_processed += 1
                    m = []
                    for fieldname in v.fields:
                        if items.has_key(fieldname):
                            m.append(items[fieldname])
                        elif fieldname != v.pk:
                            m.append(None)
                    fieldvalues.append(m)

                if self.debug_mode:
                    logging.debug("Executing insert: %s" % sql)
                    for f in fieldvalues:
                        logging.debug(str(f))

                self.sql_calls += 1
                try:
                    self.cursor.executemany(sql, fieldvalues)
                except Exception, e:
                    raise InsertManyException(e, tablename, sql, fieldvalues)
            v.reset()

    def get_items(self, tablename, where = None, order_by = None):
        """
        This is equal to django`s model.objects.values().
        """
        keys = self.registered_objects[tablename].fields
        tablename = self.registered_objects[tablename].tablename
        sql = "select * from %s %s %s" % (tablename, where and "where %s" % where or '', order_by and 'order by %s' % order_by or '')
        self.cursor.execute(sql)
        return self.yield_results(self.cursor, keys)

    def yield_results(self, cursor, keys):
        for result in cursor.fetchall():
            result_dict = {}
            assert len(keys) == len(result), "Number of fields and returned columns does not match."
            for i in range(0, len(keys)):
                result_dict[keys[i]] = result[i]
            yield result_dict                

    def flush(self):
        self.close()

    def close(self):
        self.execute_sql()
        
##########################################################################################
#
#                               Django specific code
#
##########################################################################################

DJANGO_SUPPORT = False
try:
    from django.db.models.fields import DateField
    from django.db.models.fields.related import ForeignKey
    from django.db.models.loading import get_models, get_app
    from django.db import connection
    from django.db import DEFAULT_DB_ALIAS
    DJANGO_SUPPORT = True    
except ImportError:
    pass
        
import types

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
    
class DelayedExecutor(DelayedSqlExecutor):
    """
    A Django specific version of the DelayedSqlExecutor.
    """

    def __init__(self, item_limit = 1000, paramtoken = '%s'):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        
        cursor = connection.cursor()
        super(DelayedExecutor, self ).__init__(cursor, item_limit, paramtoken)

    def values_factory_for_model(self, model):
        """
        Produces a dictionary with fieldnames from a Django model as keys.
        If any field has defined a default value it will be set in the dictionary.
        """
        
        result = {}
        for key in self.registered_objects[model._meta.object_name].fields:
            result[key] = get_defaultvalue_for_field_from_model(model, key)
        return result
    
    def add_objects_from_app(self, app_name, model_name = None):
        "Adds tables found in models related to a specified app or for just one model if the model_name is specified."
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        
        for model in get_models(get_app(app_name)):
            if model_name and model_name != model._meta.object_name:
                continue
            
            self.add_model(model)

    def add_model(self, model):
        "Adds a table to insert/update based on a Django model"
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        
        if not self.registered_objects.has_key(model._meta.object_name):
            self.add_object(model._meta.db_table, pk = model._meta.pk.name, keyname = model._meta.object_name)
        
    def add_item(self, model, values):
        "Adds a dictionary with values to insert/update for a specific model."
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        super(DelayedExecutor, self).add_item(model._meta.object_name, values)

class ModelDelayedExecutor(DelayedExecutor):
    """
    A helper-class for working with a specific Django model and DSE.
    """

    def __init__(self, model, item_limit = 1000, paramtoken = '%s'):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')

        super(ModelDelayedExecutor, self ).__init__(item_limit, paramtoken)
        self.model = model
        self.add_model(model)
        self.defaults = self.values_factory_for_model(self.model)
        self.defaults_defined = len([v for v in self.defaults.values() if v])        
        self.pk = self.registered_objects[model._meta.object_name].pk

    def add_item(self, values):
        "Adds a dictionary with values to insert/update"
        # Updates:
        if values.get('id', None):
            super(ModelDelayedExecutor, self).add_item(self.model, values)

        # Inserts, we check to see if there are any default values defined for this model, and add those if missing
        # Will always insert values into all columns
        else:
            final_values = {}
            if self.defaults_defined:
                for k,v in self.defaults.items():
                    if callable(v):
                        final_values[k] = v()
                    else:
                        final_values[k] = v
            final_values.update(values)
            super(ModelDelayedExecutor, self).add_item(self.model, final_values)

    def get_items(self, where = None, order_by = None):
        """
        Returns a generator for records related to this model.
        Can be filtered using the where-argument, ex. age < 20 and
        ordered using the order_by-argument.

        This is equal to django`s model.objects.values() just a way to use plain SQL-syntax ( age = 20 ) instead of django syntax ( age__eq = 20 ).
        """
        return super(ModelDelayedExecutor, self).get_items(self.model._meta.object_name, where, order_by)

    def __iter__(self):
        for item in self.model.objects.all().values():
            yield item

    def values_factory(self):
        """
        Returns a dictionary with keys corresponding to fields in the associated model
        and automatically sets any defined default values defined in the model.
        """
        return self.values_factory_for_model(self.model)