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
        if values.get(self.pk, None):
            self.update_items.append(values)
        else:
            if values.has_key(self.pk) and not values.get(self.pk):
                del values[self.pk]
            self.insert_items.append(values)

    @property
    def itemCount(self):
        return len(self.update_items) + len(self.insert_items)

class ObjectNotRegistered(Exception): pass

class DelayedSqlExecutor(object):

    def __init__(self, cursor, item_limit = 1000, paramtoken = '%s'):
        self.cursor = cursor
        self.item_limit = item_limit
        self.paramtoken = paramtoken
        self.objects = {}
        self.debug_mode = False
        self.sql_calls = 0
        self.records_processed = 0

    def addObject(self, tablename, pk = 'id', keyname = None):
        if not keyname:
            keyname = tablename
        #self.cursor.execute('select * from %s where %s = null' % (tablename, pk))
        self.cursor.execute('select * from %s' % tablename)
        fields = []
        if self.debug_mode:
            print "Fields found for table %s:" % tablename,
        for idx, field_attrs in enumerate(self.cursor.description):
            fields.append(field_attrs[0])
            if self.debug_mode:
                print field_attrs[0],
        if self.debug_mode:
            print
    
        if self.debug_mode:
            logging.debug("AddObject: %s. Fields = %s" % (tablename, fields))

        self.objects[keyname] = TableObject(tablename, fields, pk)
    
    @property
    def totalItemCount(self):
        total_items = 0
        to = None
        for k,v in self.objects.items():
            total_items += v.itemCount
        return total_items

    def addItem(self, tablename, values):
        to = self.objects.get(tablename, None)
        if not to:
            raise ObjectNotRegistered(tablename)
        
        if self.totalItemCount >= self.item_limit:
            self.executeSql()

        to.add(values)

    def executeSql(self):
        for k,v in self.objects.items():
            tablename = self.objects[k].tablename
            if v.update_items:
                sql = ['update %s set' % tablename]
                m = []
                for fieldname in v.fields:
                    if fieldname == v.pk:
                        continue
                    m.append("%s = %s" % (fieldname, self.paramtoken))
                sql.append(',\n'.join(m))
                sql.append('where %s = %s' % (v.pk, self.paramtoken))
                fieldvalues = []
                for items in v.update_items:
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
                        
                self.sql_calls += 1
                try:
                    self.cursor.executemany('\n'.join(sql), fieldvalues)
                except Exception, e:
                    print "Error executing SQL:", e
                    print sql
                    print fieldvalues[0]

            if v.insert_items:
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
                    print "Error executing SQL:", e
                    print sql
                    print fieldvalues[0]
            v.reset()

    def getItems(self, tablename, where = None, order_by = None):
        keys = self.objects[tablename].fields
        tablename = self.objects[tablename].tablename
        sql = "select * from %s %s %s" % (tablename, where and "where %s" % where or '', order_by and 'order by %s' % order_by or '')
        self.cursor.execute(sql)
        for result in self.cursor.fetchall():
            result_dict = {}
            assert(len(keys) == len(result), "Number of fields and returned columns does not match.")
            for i in range(0, len(keys)):
                result_dict[keys[i]] = result[i]
            yield result_dict                

    def flush(self):
        self.close()

    def close(self):
        self.executeSql()
        
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
    DJANGO_SUPPORT = True    
except ImportError:
    pass
        
#http://djangosnippets.org/snippets/199/
def instance_dict(instance, key_format=None):
    """
    Returns a dictionary containing field names and values for the given
    instance
    """
    if key_format:
        assert '%s' in key_format, 'key_format must contain a %s'
    key = lambda key: key_format and key_format % key or key

    pk = instance._get_pk_val()
    d = {}
    for field in instance._meta.fields:
        attr = field.name
        value = getattr(instance, attr)
        if value is not None:
            if isinstance(field, ForeignKey):
                value = value._get_pk_val()
            elif isinstance(field, DateField):
                value = value.strftime('%Y-%m-%d')
        d[key(attr)] = value
    for field in instance._meta.many_to_many:
        if pk:
            d[key(field.name)] = [
                obj._get_pk_val()
                for obj in getattr(instance, field.attname).all()]
        else:
            d[key(field.name)] = []
    return d

import types

def get_defaultvalue_for_field_from_model(model, field):
    for f in model._meta._field_name_cache:
        if field == f.name:
            if type(f.default) == types.ClassType:
                if f.default.__name__ == 'NOT_PROVIDED':
                    return None
            return f.default
    return None
    
class DelayedExecutor(DelayedSqlExecutor):

    def __init__(self, item_limit = 1000, paramtoken = '%s'):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        
        cursor = connection.cursor()
        super(DelayedExecutor, self ).__init__(cursor, item_limit, paramtoken)

    def valuesFactoryForModel(self, model):
        
        result = {}
        for key in self.objects[model._meta.object_name].fields:
            result[key] = get_defaultvalue_for_field_from_model(model, key)
        return result
    
    def addObjectsFromApp(self, app_name, model_name = None):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        
        for model in get_models(get_app(app_name)):
            if model_name and model_name != model._meta.object_name:
                continue
            
            self.addModel(model)

    def addModel(self, model):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        
        if not self.objects.has_key(model._meta.object_name):
            self.addObject(model._meta.db_table, pk = model._meta.pk.name, keyname = model._meta.object_name)
        
    def addItem(self, model, values):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')
        super(DelayedExecutor, self).addItem(model._meta.object_name, values)

class ModelDelayedExecutor(DelayedExecutor):

    def __init__(self, model, item_limit = 1000, paramtoken = '%s'):
        if not DJANGO_SUPPORT:
            raise Exception('No django support.')

        super(ModelDelayedExecutor, self ).__init__(item_limit, paramtoken)
        self.model = model
        self.addModel(model)
        self.defaults = self.valuesFactoryForModel(self.model)
        self.defaults_defined = len([v for v in self.defaults.values() if v])

    def addItem(self, values):
        final_values = {}
        if self.defaults_defined:
            for k,v in self.defaults.items():
                if callable(v):
                    final_values[k] = v()
                else:
                    final_values[k] = v
        if self.debug_mode:
            print final_values
        final_values.update(values)
        super(ModelDelayedExecutor, self).addItem(self.model, final_values)

    def getItems(self, where = None, order_by = None):
        return super(ModelDelayedExecutor, self).getItems(self.model._meta.object_name, where, order_by)