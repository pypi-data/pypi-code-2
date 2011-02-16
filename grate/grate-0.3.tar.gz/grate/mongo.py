import os
import uuid
import hashlib
import functools
from datetime import datetime
import mongoengine
from mongoengine import (Document, BinaryField, StringField, ListField,
    ReferenceField, BooleanField, GenericReferenceField, EmbeddedDocument,
    EmbeddedDocumentField, IntField, DateTimeField, DictField)
from twisted.conch.ssh import keys
from twisted.python import log
from grate import server
from grate.access import Entity, EntityCollection, EntityAccess
from grate.atomic import atomic
from grate.djangocompat import DjangoUser

# WTF, man, WTF
import pymongo.dbref
import pymongo.objectid
import pymongo.son
import pymongo.code
import gflags

gflags.DEFINE_string('mongo_dbname', 'grate', 'The database name.')
gflags.DEFINE_string('mongo_username', None, 'The mongo username.')
gflags.DEFINE_string('mongo_password_file', None, 'The path to the file '
                     'containing the password to the mongo database.')
gflags.DEFINE_string('mongo_host', 'localhost', 'Host of the mongo database.')
gflags.DEFINE_string('mongo_port', 27017, 'Port of the mongo database.')
FLAGS = gflags.FLAGS


def set_decorator(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return set(f(*args, **kwargs))
    return wrapper


class GrateConfigDocument(Document):
    meta = {'collection': 'grateconfig'}
    config = DictField(default={})

    @classmethod
    def get_config(cls):
        """
        :returns: The singleton config object.
        """
        cfg = cls.objects.first()
        if not cfg:
            cfg = cls()
            cfg.save(safe=True)
        if not cfg.config:
            cfg.config = {}
        return cfg

    def git_url(self, user, path):
        """
        :returns: The correct git url for the user and the repository path
            (relative), if the host and port for the ssh daemon is
            configured.
        """
        port = self.config['port'] if self.config.has_key('port') else None
        host = self.config['host'] if self.config.has_key('host') else None
        if not host and not port:
            return None
        if port == 22:
            return '%s@%s:%s' % (user, host, path)
        else:
            return 'ssh://%s@%s:%d/%s' % (user, host, port, path)


class GrateConfig(object):
    singleton = None
    # Use a descriptor to delay the assignment.
    # I cannot write:
    #     objects = GrateConfigDocument.objects
    # because this causes errors due to import/database connecting
    class _Thunk(object):
        def __get__(self, instance, owner):
            return GrateConfigDocument.objects
    objects = _Thunk()

    def __init__(self, **kwargs):
        """
        :param doc: The :class:`GrateConfigDocument`
        """
        self.doc = GrateConfigDocument.get_config()
        self.doc.config.update(kwargs)

    @classmethod
    def get_config(cls):
        """
        :returns: The singleton config object.
        """
        if not cls.singleton:
            cls.singleton = cls()
        return cls.singleton

    def __getattr__(self, name):
        try:
            return self.doc.config[name]
        except KeyError:
            return getattr(self.doc, name)

    def __setattr__(self, name, value):
        if not name == 'doc':
            self.doc.config[name] = value
        else:
            self.__dict__[name] = value

    def __delattr__(self, name):
        del self.doc.config[name]

    @classmethod
    def drop_collection(cls, *args, **kwargs):
        return GrateConfigDocument.drop_collection(*args, **kwargs)


class Group(EntityCollection):
    # The name group is special to Mongo, do not use.
    meta = {'collection': 'crowd'}
    name = StringField(max_length=50, unique=True, required=True)
    owned_repos = ListField(ReferenceField('Repo'), default=[])

    ENTITY_NAMESPACE = 'group'
    VALID_ACCESS_MAP = {
        'member': 500,
        'admin': 1000,
    }

    @set_decorator
    def admin_groups(self):
        for g in Group.objects(owner=self):
            yield g
            for h in g.owned_groups():
                yield h
        for a in EntityAccess.objects(ns=Group.ENTITY_NAMESPACE, entity=self):
            if a.access == 1000:
                yield a.provider
                for g in a.provider.admin_groups():
                    yield g

    @atomic
    def add_access(self, entity, access):
        ea, created = super(Group, self).add_access(entity, access)
        if not created or entity not in self.entities:
            self.entities.append(entity)
            self.save(safe=True)

    def add_repo(self, repo):
        # FIXME DUPED
        """
        :param repo: Repo
        """
        if repo not in self.owned_repos:
            self.owned_repos.append(repo)
            return True
        return False

    @set_decorator
    def owned_groups(self):
        for g in Group.objects(owner=self):
            yield g
            for h in g.owned_groups():
                yield h

    def get_groups(self):
        for a in EntityAccess.objects(ns=Group.ENTITY_NAMESPACE, entity=self):
            g = a.provider
            yield g
            for h in g.get_groups():
                yield h

    def get_entities(self):
        for a in EntityAccess.objects(ns=Group.ENTITY_NAMESPACE, provider=self):
            yield a.id, a.entity, self.get_access_name(a.access)

    def __repr__(self):
        return '<Group %s>' % self.name

    def __unicode__(self):
        return self.name

    __str__ = __unicode__


class User(DjangoUser):
    meta = {'collection': 'user'}
    emails = ListField(StringField(max_length=50))
    keys = ListField(ReferenceField('PublicKey'), default=[])
    owned_repos = ListField(ReferenceField('Repo'), default=[])

    def __contains__(self, entity):
        return self == entity

    @set_decorator
    def owned_groups(self):
        for g in Group.objects(owner=self):
            yield g
            for h in g.owned_groups():
                yield h

    @set_decorator
    def admin_groups(self):
        for g in Group.objects(owner=self):
            yield g
            for h in g.owned_groups():
                yield h
        for a in EntityAccess.objects(ns=Group.ENTITY_NAMESPACE, entity=self):
            if a.access == 1000:
                yield a.provider
                for g in a.provider.admin_groups():
                    yield g

    def get_groups(self):
        for a in EntityAccess.objects(ns=Group.ENTITY_NAMESPACE, entity=self):
            g = a.provider
            yield g
            for h in g.get_groups():
                yield h

    def add_repo(self, repo):
        """
        :param repo: Repo
        """
        if repo not in self.owned_repos:
            self.owned_repos.append(repo)
            return True
        return False

    def add_key(self, key):
        """
        Add the given key to this user.

        :param key: A PublicKey.
        :return: True if the key is added. False if the key is a duplicate.
        :rtype: bool
        """
        if key not in self.keys:
            self.keys.append(key)
            return True
        return False

    def all_repos(self):
        return EntityAccess.get_providers(Repo.ENTITY_NAMESPACE, self)


class Repo(EntityCollection):
    meta = {'collection': 'repo'}
    name = StringField(regex=r'^[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*$',
        max_length=100, required=True, unique=True)
    is_public = BooleanField(default=False, required=True)
    aliases = ListField(StringField(max_length=100))

    ENTITY_NAMESPACE = 'repo'
    VALID_ACCESS_MAP = {
        'member': 50,
        'watcher': 10,
        'admin': 100,
    }

    def git_url(self, user):
        cfg = GrateConfig.get_config()
        return cfg.git_url(user, self.name)

    @atomic
    def add_access(self, entity, access):
        ea, created = super(Repo, self).add_access(entity, access)
        if not created or entity not in self.entities:
            self.entities.append(entity)
            self.save(safe=True)

    @classmethod
    def create(cls, name, owner, is_public):
        # FIXME make this atomic
        repo, created = cls.objects.get_or_create(name=name,
            defaults={'owner': owner, 'is_public': is_public})
        if created:
            owner.add_repo(repo)
            owner.save(safe=True)
        return repo

    def get_path(self, root):
        return os.path.join(root, *self.name.split('/'))

    @classmethod
    def get_from_path(cls, path):
        path = path.strip()
        return cls.objects(name=path).first()

    @atomic
    def remove_access(self, entity):
        super(Repo, self).remove_access(entity)

    def get_access_list(self):
        for a in EntityAccess.objects(ns=self.ENTITY_NAMESPACE, provider=self):
            level = self.get_access_name(a.access)
            yield {'id': a.id, 'entity': a.entity, 'access': level}

    def get_access(self, user):
        access = self.get_numeric_access(user)
        if access >= 50:
            return 'rw'
        elif access >= 10:
            return 'r'
        return ''

    def __str__(self):
        return self.name


class PublicKey(Document):
    data = BinaryField(max_bytes=1000, unique=True, required=True)
    user = ReferenceField(User, required=True)

    def __init__(self, *args, **kwargs):
        super(PublicKey, self).__init__(*args, **kwargs)
        # The key cache.
        self._key_cache = None

    @classmethod
    def fromString(cls, data):
        """
        :param data: A string like
            ssh-rsa BASE64DATA (optional-username)
        :rtype: :class:`PublicKey`
        """
        pubkey = keys.Key.fromString(data)
        return cls(data=pubkey.blob())

    @classmethod
    def fromKey(cls, key):
        """
        :param key: An instance of twisted.conch.ssh.keys.Key
        :rtype: :class:`PublicKey`
        """
        return cls(data=key.blob())

    def __getattr__(self, name):
        if name == 'key':
            if not self._key_cache:
                # Construct the key object cache from the blob.
                self._key_cache = keys.Key.fromString(self.data, type='BLOB')
            return self._key_cache
        return super(PublicKey, self).__getattr__(name)

    def __setattr__(self, name, value):
        # data is set-once/read-only
        if name == 'data' and self.data:
            raise AttributeError
        if name == 'user' and self.user:
            raise AttributeError
        super(PublicKey, self).__setattr__(name, value)

    def fingerprint(self):
        return self.key.fingerprint()

    def __str__(self):
        return self.fingerprint()


def initialize():
    password_file = FLAGS.mongo_password_file
    password = None
    if password_file:
        password = open(FLAGS.mongo_password_file).read().rstrip('\r\n')
    try:
        mongoengine.connect(FLAGS.mongo_dbname, **{
            'username': FLAGS.mongo_username,
            'password': password,
            'host': FLAGS.mongo_host,
            'port': FLAGS.mongo_port,
        })
    except Exception, e:
        log.err(e)
