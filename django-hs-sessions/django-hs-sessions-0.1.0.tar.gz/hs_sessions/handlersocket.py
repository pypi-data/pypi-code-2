"""
HandlerSocket backend for sessions in django.
Requires pyhs handlersocket bindings.
"""
import datetime
from django.conf import settings
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.core.exceptions import SuspiciousOperation
from django.db import DEFAULT_DB_ALIAS
from django.utils.encoding import force_unicode

from pyhs.manager import Manager
from django.db import models

class SessionStore(SessionBase):
    """
    Implements HandlerSocket session store. It's only valid storage if you are
    using mysql as database engine.
    """
    def __init__(self, session_key=None):
        """
        Initialize pyhs manager, check settings for sanity and pre-cache some
        of them.
        """
        dbs = settings.DATABASES[DEFAULT_DB_ALIAS]
        self._fields_for_index = ['session_key', 'session_data', 'expire_date']
        
        if not 'mysql' in dbs['ENGINE']:
            raise Exception()

        self.db_name = dbs['NAME']
        self.table_name = Session._meta.db_table
        self._session_cache = {}

        self.manager = Manager( [('inet', dbs['HOST'] or 'localhost', 9998)],
                                [('inet', dbs['HOST'] or 'localhost', 9999)])

        super(SessionStore, self).__init__(session_key)

    def load(self):
        """
        Load session data via handlersocket.
        """
        try:
            raw = self.manager.get(self.db_name, self.table_name, 
                    self._fields_for_index, self.session_key)
            
            if raw:
                response = dict(raw)
                
                # low-level check if session is expired
                if datetime.datetime.now() > \
                    models.DateTimeField().to_python(response['expire_date']):
                    raise Session.DoesNotExist()
                
                return self.decode(force_unicode(response['session_data']))
            else:
                raise Session.DoesNotExist()
                
        except (Session.DoesNotExist, SuspiciousOperation):
            self.create()
            return {}

    def exists(self, session_key):
        """
        Check if session exists.
        """
        return bool(self.manager.get(self.db_name, self.table_name, 
                    self._fields_for_index, session_key))

    def create(self):
        """
        Create session.
        """
        while True:
            self.session_key = self._get_new_session_key()
            try:
                # Save immediately to ensure we have a unique entry in the
                # database.
                self.save(must_create=True)
            except CreateError:
                # Key wasn't unique. Try again.
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        """
        Save session via handlersocket.
        """
        if self.exists(self.session_key):
            if must_create:
                raise CreateError
                
            self.manager.update(
                self.db_name,
                self.table_name,
                '=', 
                self._fields_for_index,
                [self.session_key],
                [   self.session_key, 
                    self.encode(self._get_session(no_load=must_create)),
                    str(self.get_expiry_date())]
            )
        else:
            self.manager.insert(
                self.db_name,
                self.table_name,
                [   ('session_key', self.session_key), 
                    ('session_data', self.encode(
                        self._get_session(no_load=must_create))), 
                    ('expire_date', str(self.get_expiry_date()))],
            )

    def delete(self, session_key=None):
        """
        Delete session via handlersocket.
        """
        if session_key is None:
            if self._session_key is None:
                return
            session_key = self._session_key

        self.manager.delete(
            self.db_name,
            self.table_name,
            '=', 
            self._fields_for_index,
            [session_key]
        )
