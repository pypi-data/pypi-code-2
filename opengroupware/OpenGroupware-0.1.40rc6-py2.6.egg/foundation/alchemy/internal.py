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
from datetime       import datetime
from time           import time
from sqlalchemy     import *
from base           import *


class ObjectInfo(Base):
    """ Object Info Entry """
    __tablename__ = 'obj_info'
    object_id = Column("obj_id", Integer,
                        primary_key=True)
    kind      = Column("obj_type", String(255))

    def __init__(self, object_id, kind):
        self.object_id = object_id
        self.kind = kind


class ObjectLink(Base):
    """ An OpenGroupare Object Link object """
    __tablename__       = 'obj_link'
    __entityName__      = 'objectLink'
    __internalName__    = 'ObjectLink' # Correct?
    object_id           = Column("obj_link_id", Integer,
                                Sequence('key_generator'),
                                primary_key=True)

    kind                = Column("link_type", String(50))
    label               = Column("label", String(255))
    source_id           = Column("source_id", Integer)
    target_id           = Column("target_id", Integer)

    def __init__(self, source, target, kind, label):
        # TODO: Throw exception if target or source is None
        self.kind = kind
        self.label = label
        self.source_id = source
        self.target_id = target

    def __eq__(self, other):
        if (isinstance(other, int)):
            return self.object_id == other
        elif (isinstance(other, ObjectLink)):
            return (self.kind == other.kind and
                     self.source_id == other.source_id and
                     self.target_id == toher.target_id)
        elif (isinstance(other, dict)):
            return (self.kind == other.get('kind', None) and
                     self.source_id == other.get('source_id', None) and
                     self.target_id == other.get('target_id', None))
        else:
            return False


class ACL(Base):
    """ An OpenGroupare Document object """
    __tablename__       = 'object_acl'
    __entityName__      = 'acl'
    __internalName__    = 'ACL' # Correct?
    object_id           = Column("object_acl_id", Integer,
                                Sequence('key_generator'),
                                primary_key=True)
    action              = Column("action", String(10))
    parent_id           = Column("object_id", Integer,
                                 nullable=False)
    context_id          = Column("auth_id", Integer)
    sort_key            = Column('sort_key', Integer)
    permissions         = Column("permissions", String(50))

    def __init__(self, parent_id, context_id, permissions=None, action='allowed'):
        self.parent_id = parent_id
        self.context_id = context_id
        if (permissions is not None):
            self.permissions = permissions.strip().lower()
        else:
            self.permissions = None
        self.action = action
        self.sort_key = 0


class Team(Base):
    """ An OpenGroupare Team object """
    __tablename__       = 'team'
    __entityName__      = 'Team'
    __internalName__    = 'Team'
    object_id           = Column("company_id",
                                Sequence('key_generator'),
                                ForeignKey('log.object_id'),
                                ForeignKey('object_acl.object_id'),
                                primary_key=True)
    name                = Column("description", String(255))
    is_locality         = Column("is_location_team", Integer)
    version             = Column("object_version", Integer)
    email               = Column("email", String(100))
    owner_id            = Column("owner_id", Integer)

    def get_display_name(self):
        return self.name


class AuditEntry(Base):
    """ An OpenGroupware Audit Object """
    __tablename__        = 'log'
    __entityName__       = 'logEntry'
    __internalName__     = 'Log' #?
    object_id       = Column("log_id", Integer,
                              Sequence('key_generator'),
                              primary_key=True)
    context_id      = Column("object_id", Integer,
                              nullable=False)
    datetime       = Column("creation_date", DateTime)
    message        = Column("log_text", Text)
    action         = Column("action", String(100))
    actor_id       = Column("account_id", Integer)

    def __init__(self):
        self.datetime = datetime.now()

class ProcessLogEntry(Base):
    """ An OpenGroupware Audit Object """
    __tablename__        = 'process_log'
    __entityName__       = 'processLogEntry'
    __internalName__     = 'processLogEntry'
    entry_id       = Column("entry_id", Integer,
                            Sequence('process_log_entry_id_seq'),
                            primary_key=True)
    process_id     = Column("process_id", Integer, nullable=False)
    timestamp      = Column("time_stamp", Numeric, nullable=False)
    message        = Column("message", Text)
    stanza         = Column("stanza", String(32))
    source         = Column("source", String(64))
    uuid           = Column("uuid", String(64))
    category       = Column("category", String(15))

    def __init__(self, source, process_id, message, stanza=None, uuid=None, timestamp=None, category='undefined'):
        if timestamp is None:
            self.timestamp = time()
        else:
            self.timestamp = timestamp
        self.source = source
        self.process_id = process_id
        self.message = message
        self.category = category
        self.uuid = uuid
        self.stanza = stanza


class CTag(Base):
    """ An OpenGroupware CTag Object """
    __tablename__        = 'ctags'
    __entityName__       = 'ctag'
    __internalName__     = 'ctag'
    entity         = Column("entity",String(12), primary_key=True)
    ctag           = Column("ctag", Integer, nullable=False)
