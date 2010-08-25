#!/usr/bin/python
# Copyright (c) 2009 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import io, os
from log import *
import ConfigParser, logging, foundation
from sqlalchemy                 import *
from sqlalchemy.orm             import sessionmaker
from coils.foundation           import *
from defaultsmanager            import DefaultsManager

Session = sessionmaker()

def _parse_default_as_bool(value):
    if (values is None):
        return False
    if (values == 'YES'):
        return True
    return False

class Backend(object):
    _engine   = None
    _config   = None
    _bundles  = None
    _session  = None
    _auth     = None
    _fs_url   = None
    _log      = None
    _defaults = None

    @staticmethod
    def __alloc__(**params):
        if (Backend._config is None):
            # TODO: Allow to be modified
            Backend._extra_modules = params.get('extra_modules', [ ])
            Backend._banned_modules = params.get('banned_modules', [ ])
            foundation.STORE_ROOT = params.get('store_root', '/var/lib/opengroupware.org')
            Backend._fs_url = '{0}/fs'.format(foundation.STORE_ROOT)
            # Open defaults
            sd = ServerDefaultsManager()

            # TODO: Read from defaults
            log_filename = params.get('log_file', '/var/log/coils.log')
            log_level = LEVELS.get('DEBUG', logging.NOTSET)
            logging.basicConfig(filename=log_filename, level=log_level)
            Backend._log = logging
            logging.debug('Backend initialized')

    def __init__(self, **params):
        if (Backend._config is None):
            Backend.__alloc__(**params)

    @staticmethod
    def _parse_default_as_bool(value):
        if (values is None):
            return False
        if (values == 'YES'):
            return True
        return False

    @staticmethod
    def db_session():
        if (Backend._engine is None):
            sd = ServerDefaultsManager()
            Backend._engine = create_engine(sd.orm_dsn, **{'echo': sd.orm_logging})
            Session.configure(bind=Backend._engine)
        #session = Session()
        return Session()
        #return Backend._session

    @staticmethod
    def get_logic_bundle_names():
        #TODO: Load from config
        if (Backend._bundles is None):
            modules = [ 'coils.logic.foundation',
                        'coils.logic.account', 'coils.logic.address',
                        'coils.logic.blob', 'coils.logic.contact',
                        'coils.logic.enterprise', 'coils.logic.facebook',
                        'coils.logic.project', 'coils.logic.pubsub',
                        'coils.logic.schedular', 'coils.logic.task',
                        'coils.logic.team', 'coils.logic.twitter',
                        'coils.logic.workflow' ]
            modules.extend(Backend._extra_modules)
            for name in Backend._banned_modules:
                if name in modules:
                    modules.remove(name)
            Backend._bundles = modules
        return Backend._bundles

    @staticmethod
    def get_protocol_bundle_names():
        #TODO: Load from config
        modules = [ 'coils.protocol.dav', 'coils.protocol.freebusy',
                  'coils.protocol.proxy', 'coils.protocol.zogi' ]
        modules.extend(Backend._extra_modules)
        for name in Backend._banned_modules:
            if name in modules:
                modules.remove(name)
        return modules

    @staticmethod
    def store_root():
        return foundation.STORE_ROOT

    @staticmethod
    def fs_root():
        return Backend._fs_url

    @staticmethod
    def get_authenticator_options():
        if (Backend._auth is None):
            sd = ServerDefaultsManager()
            x = sd.string_for_default('LSAuthLDAPServer')
            if (len(x) > 0):
                Backend._log.info('Choosing LDAP for BASIC authentication backend')
                url = 'ldap://{0}/'.format(sd.string_for_default('LSAuthLDAPServer'))
                Backend._auth = { 'authentication': 'ldap',
                                  'url': url,
                                  'start_tls': 'NO',
                                  'binding': 'SIMPLE',
                                  'search_container': sd.string_for_default('LSAuthLDAPServerRoot'),
                                  'search_filter': '({0}=%s)'.format(sd.string_for_default('LDAPLoginAttributeName')),
                                  'bind_identity': sd.string_for_default('LDAPInitialBindDN'),
                                  'bind_secret': sd.string_for_default('LDAPInitialBindPW'),
                                  'uid_attribute': sd.string_for_default('LDAPLoginAttributeName') }
            else:
                Backend._log.info('Choosing database for BASIC authentication backend')
                Backend._auth = { 'authentication': 'db' }
        return Backend._auth
