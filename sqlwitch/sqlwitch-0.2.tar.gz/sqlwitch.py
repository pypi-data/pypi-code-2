from __future__ import with_statement

__all__ = ['SQLWitch', 'Insert', 'Select', 'Update', 'Delete']
__license__ = 'BSD'
__version__ = '0.2'
__author__ = "Jonas Galvez <http://jonasgalvez.com.br/>"

class SQLWitch:
    """Interface and execution context for SQL statements"""

    def __init__(self, cursor=None, connection=None):
        self.cursor = cursor
        self.connection = connection
        self.insert_fields = {}

    def sql(self):
        return self.current_command.build_sql()

    def params(self):
        params = self.current_command.params()
        flattened_params = []
        for param in params:
            if isinstance(param, (list, tuple)):
                flattened_params += param
            else:
                flattened_params.append(param)
        return flattened_params
        
    def insert(self, into):
        self.current_command = Insert(into)
        return self.current_command
        
    def select(self, *args, **kwargs):
        if type(kwargs['from_']) is str:
            kwargs['from_'] = [kwargs['from_']]
        self.current_command = Select(args, kwargs['from_'])
        return self.current_command
        
    def update(self, table):
        self.current_command = Update(table)
        return self.current_command
        
    def delete(self, from_):
        self.current_command = Delete(from_)
        return self.current_command
        
    def where(self, condition, *params):
        self.current_command._conditions.append([condition, params])
        return self

    def in_(self, *args):
        self.current_command._conditions[-1][0] += ' in '
        self.current_command._conditions[-1][0] += '(%s)' % (
            ', '.join(['%s'] * len(args))
        )
        self.current_command._conditions[-1][1] += args
        return self

    def limit(self, a, b=None):
        if b is not None:
            self.current_command.offset = a
            self.current_command.row_count = b
        elif a is not None:
            self.current_command.row_count = a

    def order_by(self, order_by):
        self.current_command.order_by = order_by
        return self
        
    def fetchone(self):
        self.execute()
        return self.cursor.fetchone()
        
    def fetchall(self):
        self.execute()
        return self.cursor.fetchall()
        
    def execute(self):
        params = self.params()
        if len(params):
            self.cursor.execute(self.current_command.build_sql(), tuple(params))
        else:
            self.cursor.execute(self.current_command.build_sql())
            
    def commit(self):
        self.connection.commit()


class Insert:
    """Generates a SQL insert statement"""
    
    def __init__(self, into):
        self.__dict__['_table'] = into
        self.__dict__['_conditions'] = []
        self.__dict__['_fields'] = {}
        
    def __enter__(self):
        return self 
        
    def __exit__(self, type, value, tb):
        pass
        
    def __call__(self):
        return self
        
    def __setattr__(self, name, value):
        self._fields[name] = value
        
    def __getattr__(self, name):
        return self._fields[name]
        
    __getitem__ = __getattr__
    __setitem__ = __setattr__

    def build_sql(self):
        sql = []
        sql.append('insert into %s' % self._table)
        sql.append('(%s)' % ', '.join([field for field in self._fields]))
        sql.append('values')
        sql.append('(%s);' % ', '.join(['%s' for field in self._fields]))
        return ' '.join(sql)

    def params(self):
        return self._fields.values()


class Select:
    """Generates a SQL select statement"""
    
    def __init__(self, fields, tables):
        self.fields = fields
        self.tables = tables
        self._conditions = []
        self.order_by = None
        self.offset = None
        self.row_count = None
        
    def __enter__(self):
        return self 
        
    def __exit__(self, type, value, tb):
        pass
        
    def __call__(self):
        return self
        
    def where(self, condition, *params):
        self._conditions.append([condition, params])
        return self
        
    def in_(self, *args):
        self._conditions[-1][0] += ' in '
        self._conditions[-1][0] += '(%s)' % (
            ', '.join(['%s'] * len(args))
        )
        self._conditions[-1][1] += args
        return self

    def order_by(self, order_by):
        self.order_by = order_by
        return self
        
    def limit(self, a, b=None):
        if b is not None:
            self.offset = a
            self.row_count = b
        elif a is not None:
            self.row_count = a
        
    def build_sql(self):
        sql = []
        sql.append('select')
        sql.append(', '.join(self.fields))
        sql.append('from')
        sql.append(', '.join(self.tables))
        if len(self._conditions):
            conditions = []
            for condition in self._conditions:
                conditions.append(condition[0])
            sql.append('where')
            sql.append(' and '.join(conditions))
        if self.order_by is not None:
            sql.append('order by %s' % self.order_by)
        if self.row_count is not None and self.offset is not None:
            sql.append('limit %s, %s' % (self.offset, self.row_count))
        elif self.row_count is not None:
            sql.append('limit %s' % self.row_count)
        return '%s;' % ' '.join(sql)

    def params(self):
        return [condition[1] for condition in self._conditions]


class Update:
    """Generates a SQL update statement"""
    
    def __init__(self, table):
        self.__dict__['_table'] = table
        self.__dict__['_conditions'] = []
        self.__dict__['_fields'] = {}
        
    def __enter__(self):
        return self 
        
    def __exit__(self, type, value, tb):
        pass
        
    def __call__(self):
        return self
        
    def __setattr__(self, name, value):
        self._fields[name] = value
        
    def __getattr__(self, name):
        return self._fields[name]

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    
    def where(self, condition, *params):
        self._conditions.append([condition, params])
        return self
    
    def build_sql(self):
        sql = []
        sql.append('update %s set' % self._table)
        sql.append(', '.join([('%s = %%s' % field) for field in self._fields]))
        if len(self._conditions):
            conditions = []
            for condition in self._conditions:
                conditions.append(condition[0])
            sql.append('where')
            sql.append(' and '.join(conditions))
        return '%s;' % ' '.join(sql)
        
    def params(self):
        return self._fields.values() + [
            condition[1] for condition in self._conditions
        ]


class Delete:
    """Generates a SQL delete statement"""
    
    def __init__(self, table):
        self.table = table
        self._conditions = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, type, value, tb):
        pass
    
    def __call__(self):
        return self
        
    def where(self, condition, *params):
        self._conditions.append([condition, params])
        return self
        
    def build_sql(self):
        sql = []
        sql.append('delete from %s' % self.table)
        if len(self._conditions):
            conditions = []
            for condition in self._conditions:
                conditions.append(condition[0])
            sql.append('where')
            sql.append(' and '.join(conditions))
        return '%s;' % ' '.join(sql)
    
    def params(self):
        return [condition[1] for condition in self._conditions]
