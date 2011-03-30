#
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
import sys, time, logging, time, uuid
from sqlalchemy        import *
from pytz              import timezone
from datetime          import datetime, timedelta
from coils.foundation  import *
from exception         import *
from ldapauthenticator import LDAPAuthenticator
from dbauthenticator   import DBAuthenticator
from bundlemanager     import BundleManager
from accessmanager     import AccessManager
from linkmanager       import LinkManager
from propertymanager   import PropertyManager
from lockmanager       import LockManager
from command           import Command
from packet            import Packet

class Context(object):

    __slots__ = ('_orm', '_pm', '_log', '_email', '_queue',
                  '_login', '_context_ids', '_timezone', '_defaults',
                  '_meta', '_cluster_id', '_lockman')

    _typeManager   = None
    _mapper        = None
    _accessManager = None
    _orm           = None

    def __init__(self, metadata, broker=None):
        self._orm        = None
        self._dm         = None  # Defaults Manager
        self._lm         = None  # Link Manager
        self._pm         = None  # Property Manager
        self._lockman    = None  # Lock Manager
        self._cluster_id = None
        self._log        = logging.getLogger('context')
        self._email      = None
        self._login      = None
        self._queue      = [ ]
        self._meta       = metadata
        self._callbacks  = { }
        self._uuid       = str(uuid.uuid4())
        self._log.debug('Context {0} created'.format(self._uuid))
        if (Context._typeManager == None):
            Context._typeManager = TypeManager()
        if (Context._mapper == None):
            Context._mapper = BundleManager()
        if (Context._accessManager == None):
            Context._accessManager = AccessManager()
        if ('amq_broker' not in metadata) and (broker is None):
            self._log.debug('AMQ broker not available in context.')
        else:
            self._meta['amq_broker'] = metadata.get('amq_broker', broker)


    def __del__(self):
        self.close()


    def close(self):
        self._log.debug('Closing context {0}'.format(self._uuid))
        self._callbacks = { }
        if (self._orm is not None):
            self._orm.close()
            self._orm = None

    @property
    def cluster_id(self):
        if self._cluster_id is None:
            prop = self.property_manager.get_server_property('http://www.opengroupware.us/global', 'clusterGUID')
            if (prop is None):
                raise CoilsException('No cluster id has been generated for this server.')
            self._cluster_id = prop.get_value()
        return self._cluster_id

    @property
    def type_manager(self):
        return Context._typeManager

    @property
    def access_manager(self):
        return Context._accessManager

    @property
    def link_manager(self):
        if (self._lm is None):
            self._lm = LinkManager(self)
        return self._lm

    @property
    def property_manager(self):
        if (self._pm is None):
            self._pm = PropertyManager(self)
        return self._pm

    @property
    def lock_manager(self):
        if (self._lockman is None):
            self._lockman = LockManager(self)
        return self._lockman

    @property
    def log(self):
        return self._log

    @property
    def is_admin(self):
        if 10000 in self.context_ids:
            return True
        return False

    def db_session(self):
        if (self._orm is None):
            self._log.debug('Allocating new database session.')
            self._orm = Backend.db_session()
            # This is in order to help debug ORM QueuePool issues like Issue#134
            self._log.debug(self._orm.connection().engine.pool.status())
        return self._orm

    def begin(self):
        pass

    def queue_for_commit(self, source, target, data):
        self._queue.append((source, target, data))

    def commit(self):
        #self.db_session.flush()
        self._log.debug('Context commit requested.')
        self.db_session().commit()
        self._log.debug('Context commit completed.')
        if (len(self._queue) > 0):
            if (self.amq_available):
                for notice in self._queue:
                    self.send(notice[0], notice[1], notice[2])
            self._queue = [ ]
        return

    def rollback(self):
        self.db_session().rollback()
        return

    def run_command(self, command_name_x, **params):
        command = Context._mapper.get_command(command_name_x)
        if isinstance(command, Command):
            start = time.time()
            command.prepare(self, **params)
            command.run()
            command.epilogue()
            result = command.get_result()
            end = time.time()
            self._log.debug('duration of %s was %0.3f' % (command_name_x, (end - start)))
            command = None
            return result
        else:
            self._log.error('No such command as {0}'.format(command_name_x))
            raise CoilsException('No such command as {0}'.format(command_name_x))
        return None


    @property
    def defaults_manager(self):
        if (self._dm is None):
            self._dm = UserDefaultsManager(self.account_id)
        return self._dm

    def get_timezone(self):
        return timezone('UTC')

    def get_utctime(self):
       utc = timezone('UTC')
       return datetime.now(tz=utc)

    def get_timestamp(self):
        #TODO: There has to be a more efficient way to do this?!
        return int(datetime.utcnow().strftime('%s'))

    def as_localtime(self, time):
        if (time is None):
            return self.get_localtime()
        return time.astimezone(self.get_timezone())

    def get_offset_from(self, time):
        return ((86400 - self.get_timezone().utcoffset(time).seconds) * -1)

    def get_locatime(self):
       tz = self.get_timezone()
       localtime = self.get_utctime().astimezone(tz)

    @property
    def login(self):
        return self.get_login()

    def get_login(self):
        return None

    @property
    def email(self):
        if (self._login is None):
            return None
        if (self._email is None):
            if (hasattr(self._login, 'company_values')):
                for cv in self._login.company_values:
                    if (cv.name == 'email1'):
                        if (cv.string_value is not None):
                            if (len(cv.string_value) > 0):
                                self._email = cv.string_value
        return self._email

    @property
    def amq_broker(self):
        return self._meta['amq_broker']

    @property
    def amq_available(self):
        if ('amq_broker' in self._meta):
            return True
        return False

    def send(self, source, target, data, callback=None):
        if (self.amq_available):
            packet = Packet(source, target, data)
            self.amq_broker.send(packet, callback=self.callback)
            if (callback is not None):
                self._callbacks[packet.uuid] = callback
            return packet.uuid
        else:
            raise CoilsException('Service bus not available to context.')
        return None

    def callback(self, uuid, source, target, data):
        if (uuid in self._callbacks):
            if (self._callbacks[uuid](uuid, source, target, data)):
                del self._callbacks[uuid]
                return True
            else:
                return False
        self.log.warn('Request for callback on packet {0} which has no callback.'.format(uuid))

    def wait(self, timeout=1000):
        start = time.time()
        end   = start + (timeout / 1000.0)
        while ((len(self._callbacks)) > 0 and (time.time() < end)):
            self.amq_broker.wait(timeout=timeout)
        return (len(self._callbacks) > 0)

    def get_favorited_ids_for_kind(self, kind, refresh=True):
        # Anonymous doesn't have favorites
        if (self.account_id == 0):
            return [ ]
        kind = kind.lower()
        if (kind == 'contact'): kind = 'person'
        default = '{0}_favorites'.format(kind)
        if (refresh == False) and (hasattr(self, '_cache_{0}'.format(default))):
            return getattr(self, '_cache_{0}'.format(default))
        fav_ids = [int(object_id) for object_id in self.defaults_manager.default_as_list(default, [])]
        setattr(self, '_cache_{0}'.format(default), fav_ids)
        return fav_ids

    def send_administrative_notice(self, subject=None,
                                         message=None,
                                         urgency=9,
                                         category='unspecified',
                                         attachments=[]):
        # TODO: Support attachments
        try:
            self.send(None,
                      'coils.administrator/notify',
                      { 'urgency': urgency,
                        'category': category,
                        'subject': subject,
                        'message': message } )
        except Exception, e:
            self.log.error('Exception attempting to send administrative notice')
            self.log.exception(e)


class AnonymousContext(Context):
    def __init__(self, metadata = {}, broker=None):
        Context.__init__(self, metadata, broker=broker)

    @property
    def account_id(self):
        return 0

    @property
    def context_ids(self):
        return [0]

    def get_login(self):
        return 'Coils\\Anonymous'

class NetworkContext(Context):
    def __init__(self, metadata = {}, broker=None):
        Context.__init__(self, metadata, broker=broker)

    @property
    def account_id(self):
        return 8999

    @property
    def context_ids(self):
        return [8999]

    def get_login(self):
        return 'Coils\\Network'

    @property
    def email(self):
        sd = ServerDefaultsManager()
        email = sd.string_for_default('AdministrativeEMailAddress', value='root@localhost')
        return email

class AdministrativeContext(Context):

    def __init__(self, metadata = {}, broker=None):
        Context.__init__(self, metadata, broker=broker)

    @property
    def account_id(self):
        return 10000

    @property
    def context_ids(self):
        return [ 10000 ]

    def get_login(self):
        return 'Coils\\Administrator'


class AuthenticatedContext(Context):
    _auth_class   = None
    _auth_options = None
    _defaults     = None
    _timezone     = None
    _context_ids  = None

    def __init__(self, metadata, broker=None):
        Context.__init__(self, metadata, broker=broker)
        if (AuthenticatedContext._auth_options is None):
            AuthenticatedContext._auth_options = Backend.get_authenticator_options()
        if (AuthenticatedContext._auth_class is None):
            class_name = '%sAuthenticator' % AuthenticatedContext._auth_options['authentication'].upper()
            AuthenticatedContext._auth_class = eval(class_name)
        Backend._log.debug('Authentication class is {0}'.format(AuthenticatedContext._auth_class))
        self.authorizor = AuthenticatedContext._auth_class(self,
                                                           self._meta,
                                                           AuthenticatedContext._auth_options)
        if (self.authorizor.authenticated_id() is None):
            self._log.warn('Unable to authenticate sessoion')
            raise AuthenticationException('Unable to authenticate session')

    def get_login(self):
        return self._meta['authentication']['login']

    def get_defaults(self):
        if (self._defaults is None):
            self._defaults = self.run_command('account::get-defaults')
        return self._defaults

    def get_timezone(self):
        if (self._timezone is None):
            defaults = self.get_defaults()
            if (defaults.has_key('timezone')):
                self._timezone = timezone(defaults['timezone'])
            else:
                self._timezone = timezone('UTC')
        return self._timezone

    @property
    def account_id(self):
        return self.authorizor.authenticated_id()

    @property
    def context_ids(self):
        if (self._context_ids is None):
            self._context_ids = []
            self._context_ids.append(self.account_id)
            x = self.run_command('team::get', member_id = self.account_id)
            for team in x:
                self._context_ids.append(team.object_id)
        return self._context_ids


class AssumedContext(Context):
    _defaults     = None
    _timezone     = None
    _context_ids  = None

    def __init__(self, context_id, metadata = {}, broker=None):
        Context.__init__(self, metadata, broker=broker)
        self._get_login(context_id)

    def _get_login(self, context_id):
        db = self.db_session()
        query = db.query(Contact).filter(and_(Contact.object_id==context_id,
                                               Contact.is_account==1,
                                               Contact.status!='archived'))
        data = query.first()
        if (data is not None):
            self._login = data
        else:
            raise AuthenticationException('No account with id of {0}.'.format(context_id))

    def get_login(self):
        return self._login.login

    def get_defaults(self):
        if (self._defaults is None):
            self._defaults = self.run_command('account::get-defaults')
        return self._defaults

    def get_timezone(self):
        if (self._timezone is None):
            defaults = self.get_defaults()
            if (defaults.has_key('timezone')):
                self._timezone = timezone(defaults['timezone'])
            else:
                self._timezone = timezone('UTC')
        return self._timezone

    @property
    def account_id(self):
        return self._login.object_id

    @property
    def context_ids(self):
        if (self._context_ids is None):
            self._context_ids = []
            self._context_ids.append(self.account_id)
            x = self.run_command('team::get', member_id = self.account_id)
            for team in x:
                self._context_ids.append(team.object_id)
        return self._context_ids
