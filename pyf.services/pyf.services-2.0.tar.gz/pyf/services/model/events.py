from ConfigParser import SafeConfigParser
import operator
import cStringIO

from pyf.services.model import DeclarativeBase, metadata, DBSession
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import (Unicode, Integer, DateTime, TEXT, String,
                              Boolean, DECIMAL)
from sqlalchemy.orm import relation, synonym

from pyf.componentized.core import Manager as ComponentManager

from pyf.componentized import ET
import logging

from datetime import datetime

class EventOutputFile(DeclarativeBase):
    __tablename__ = "eventoutputs"
    
    id = Column(Integer, primary_key=True)
    eventtrack_id = Column(Integer,
                           ForeignKey('eventtracks.id'), nullable=True)

    eventrack = relation('EventTrack', backref='output_files')
    file_uuid = Column(String(32), nullable=False)
    creation_date = Column(DateTime, default=datetime.now)
    
    filename = Column(String(500), nullable=True)
    
    def get_file(self):
        from pyf.services.core.storage import get_storage
        if self.file_uuid:
            storage = get_storage('output')
            storage_filename = storage.get_filename(self.file_uuid)
    
            return open(storage_filename, 'rb')
        else:
            return None


class EventTrack(DeclarativeBase):
    __tablename__ = "eventtracks"
    
    id = Column(Integer, primary_key=True)
    
    # possible values for status are:
    # - pending
    # - processing
    # - post-process
    # - success
    # - failure (generic)
    # - failure-writer
    # - failure-adapter
    # - failure-extractor
    # - failure-postprocess
    status = Column(String(32), nullable=False, default='pending', index=True)
    
    progression = Column(DECIMAL)
    
    start_date = Column(DateTime)
    end_date = Column(DateTime, nullable=True)
    
    storage_file_uuid = Column(String(32), nullable=True)
    source_filename = Column(String(512), nullable=True)
    
    tube_id = Column(Integer, ForeignKey('tubes.id'))
    tube = relation('Tube', backref='events')
    dispatch_id = Column(Integer, ForeignKey('dispatchs.id'))
    dispatch = relation('Dispatch', backref='events')
    
    variant_name = Column(Unicode(50), nullable=True)
    
    flow_encoding = Column(String(10), nullable=True)

    @property
    def ordered_output_files(self):
#        output_files = list()
#        query = DBSession.query(EventOutputFile)
#        query = query.filter(EventOutputFile.eventtrack_id==self.id)
#        items = query.order_by(EventOutputFile.filename)
#        for item in items:
#            output_files.append(item)
#
#        return output_files
        return sorted(self.output_files, key=operator.attrgetter('filename'))
    
    def get_source_file(self):
        from pyf.services.core.storage import get_storage
        if self.storage_file_uuid:
            storage = get_storage('input')
            storage_filename = storage.get_filename(self.storage_file_uuid)

            return open(storage_filename, 'rb')
        else:
            return None
    
class EventHistory(DeclarativeBase):
    __tablename__ = "eventhistory"
    
    id = Column(Integer, primary_key=True)
    source = Column(String(32), nullable=False, default='user')
    eventtrack_id = Column(Integer,
                           ForeignKey('eventtracks.id'), nullable=True)
    eventrack = relation('EventTrack', backref='history')
    user_id = Column(Integer,
            ForeignKey('tg_user.user_id'), index=True, nullable=True)
    user = relation('User', backref='history')
    timestamp = Column(DateTime, default=datetime.now, index=True)
    message = Column(Unicode(5000))
    message_type = Column(Unicode(10), default='info')
    
    @property
    def display_name(self):
        return u'%s: %s' % (self.source, self.message)
    
class EventStorage(DeclarativeBase):
    """the storage table is used to manage all files on the storage.
    """
    __tablename__ = "eventstorage"
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(32), unique=True, index=True)
    dirname = Column(String(128))

    @classmethod
    def by_uuid(cls, uuid):
        return DBSession.query(cls).filter(cls.uuid==uuid).first()
