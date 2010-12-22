"HandlerSocket cache backend."

from django.core.cache.backends.base import BaseCache
from django.core.cache.backends.db import Options
from django.conf import settings
from django.utils.encoding import smart_str

from django.db import router, models
import base64, time

from pyhs.manager import Manager
from pyhs.exceptions import OperationalError

from datetime import datetime
try:
    import cPickle as pickle
except ImportError:
    import pickle

class CacheClass(BaseCache):
    def __init__(self, table, params):
        BaseCache.__init__(self, params)

        try:
            self._max_entries = int(params.get('max_entries', 300))
        except (ValueError, TypeError):
            self._max_entries = 300

        try:
            self._cull_frequency = int(params.get('cull_frequency', 3))
        except (ValueError, TypeError):
            self._cull_frequency = 3
            
        class CacheEntry(object):
            _meta = Options(table)
        self.cache_model_class = CacheEntry
        
        self._count_key = '_records_count'
        self._fields_for_index = ['cache_key', 'value', 'expires']

        db_for_read = settings.DATABASES[router.db_for_read(self.cache_model_class)]
        db_for_write = settings.DATABASES[router.db_for_write(self.cache_model_class)]

        if not 'mysql' in db_for_read['ENGINE']:
            raise Exception()

        self._read_db_name = db_for_read['NAME']
        self._write_db_name = db_for_write['NAME']
        self._table_name = table
        self._expire_index_name = '%s_expires' % table

        self.manager = Manager( [('inet', db_for_read['HOST'] or 'localhost', 9998)],
                                [('inet', db_for_write['HOST'] or 'localhost', 9999)])

    def get(self, key, default=None):
        row = self._base_get(key)
        
        if row:
            if datetime.now() > \
                models.DateTimeField().to_python(row['expires']):
                self.delete(key)
                return default
            
            return pickle.loads(base64.decodestring(row['value']))
        else:
            return default
            
    def _base_get(self, key):
        raw = self.manager.get(self._read_db_name, self._table_name, 
                self._fields_for_index, smart_str(key))

        if raw:
            return dict(raw)
        else:
            return None

    def set(self, key, value, timeout=None):
        self._base_set('set', key, value, timeout)

    def add(self, key, value, timeout=None):
        return self._base_set('add', key, value, timeout)

    def _base_set(self, mode, key, value, timeout=None):
        if timeout is None:
            timeout = self.default_timeout

        now = datetime.now().replace(microsecond=0)
        exp = datetime.fromtimestamp(time.time() + timeout).replace(microsecond=0)

        if key != self._count_key:
            self._test_cull(now)

        encoded = base64.encodestring(pickle.dumps(value, 2)).strip()
        row = self._base_get(key)
        key = smart_str(key)
        
        try:
            if row and (mode == 'set' or
                (mode == 'add' and now > \
                    models.DateTimeField().to_python(row['expires']))):

                self.manager.update(
                    self._write_db_name,
                    self._table_name,
                    '=', 
                    self._fields_for_index,
                    [key],
                    [   key, 
                        encoded,
                        str(exp)]
                )
            else:
                self.manager.insert(
                    self._write_db_name,
                    self._table_name,
                    [   ('cache_key', key), 
                        ('value', encoded), 
                        ('expires', str(exp))],
                )
                
                if key != self._count_key:
                    self._inc_counter()

        except OperationalError:
            return False
        else:
            return True

    def delete(self, key):
        deleted = self.manager.delete(
            self._write_db_name,
            self._table_name,
            '=', 
            self._fields_for_index,
            [smart_str(key)]
        )
        
        if deleted:
            self._inc_counter(-1)
            
    def _inc_counter(self, delta = 1):
        value = self.get(self._count_key)
        value = max((value or 0) + delta, 0)
        timeout = 60 * 60 * 24 * 30
        
        if value is not None:
            self.set(self._count_key, value, timeout)
        else:
            self.add(self._count_key, value, timeout)

    def has_key(self, key):
        row = self._base_get(smart_str(key))
        now = datetime.now().replace(microsecond=0)

        if row:
            return now <= models.DateTimeField().to_python(row['expires'])
        else:
            return False
        
    def _test_cull(self, now):
        num = self.get(self._count_key)
        
        if num <= self._max_entries:
            return

        deleted = self.manager.delete(
            self._write_db_name,
            self._table_name,
            '<=', 
            ['expires'],
            [str(now)],
            index_name = self._expire_index_name,
            limit = 1000000,
        )

        self._inc_counter(-deleted)
        num = num - deleted

        if self._cull_frequency == 0:
            self.clear()
        else:
            if num > self._max_entries:
                raw = self.manager.find(
                    self._read_db_name, 
                    self._table_name, 
                    '>',
                    self._fields_for_index, 
                    [''],
                    limit = num / self._cull_frequency + 1,
                    offset = num / self._cull_frequency,
                )

                deleted = self.manager.delete(
                    self._write_db_name,
                    self._table_name,
                    '<', 
                    self._fields_for_index,
                    [dict(raw[0])['cache_key']],
                    # limit = self._max_entries,
                    limit = 1000000,
                )
                
                self._inc_counter(-deleted)

    def clear(self):
        self.manager.delete(
            self._write_db_name,
            self._table_name,
            '>', 
            self._fields_for_index,
            [''],
            # limit = self._max_entries,
            limit = 1000000,
        )