from pyf.services.model import (DBSession, Tube, EventHistory, EventOutputFile, 
                             EventTrack, session_commit)

from pyjon.descriptors import Descriptor
from pyjon.utils.main import create_function
from datetime import datetime
from pyf.services.config.app_cfg import base_config

from pyjon.events import EventDispatcher
import time

from pyf.componentized import ET
    
import transaction

from pyf.services.core.storage import get_storage

import logging
logger = logging.getLogger()

import os

def create_event_track(tube,
                       storage_file_uuid="",
                       source_filename="",
                       encoding="UTF-8",
                       dispatch=None,
                       variant_name=None):
    event_track = EventTrack(tube=tube,
                             dispatch=dispatch,
                             start_date=datetime.now(),
                             storage_file_uuid=storage_file_uuid,
                             source_filename=source_filename,
                             flow_encoding=encoding,
                             variant_name=variant_name)
    DBSession.add(event_track)
    DBSession.flush()
    return event_track

def get_logger(event_track_obj):
    return EventLogger(event_track_obj.id)

class EventLogger(object):
    __metaclass__ = EventDispatcher
    def __init__(self, eventtrack_id):
        self.eventtrack_id = eventtrack_id
        self.output_files = list()
        
    def plug_on_event_source(self, event_source):
        event_source.add_listener('progress', self.progress)
        event_source.add_listener('info', self.info)
        event_source.add_listener('success', self.success)
        event_source.add_listener('failure', self.failure)
    
    def get_eventtrack(self):
        return DBSession.query(EventTrack).get(self.eventtrack_id)
    
    def progress(self, progression):
        event = self.get_eventtrack()
        if event.status != 'processing':
            self.set_status('processing')
        event.progression = progression
        DBSession.add(event)
        DBSession.flush()
        session_commit(DBSession)
        
        
    def info(self, message, message_type="info", source="process", user=None):
        event = self.get_eventtrack()
        message = EventHistory(source=source, eventtrack_id=event.id,
                               message=unicode(message), message_type=unicode(message_type),
                               user_id=(user and user.user_id or None))
        DBSession.add(message)
        DBSession.flush()
        session_commit(DBSession)
        
    
    def set_status(self, status):
        event = self.get_eventtrack()
        event.status=status
        if len(event.output_files) != len(self.output_files):
            event.output_files = self.output_files
            
        DBSession.add(event)
        DBSession.flush()
        
    def set_end_date(self):
        event = self.get_eventtrack()
        event.end_date=datetime.now()
        DBSession.add(event)
        DBSession.flush()
        
    def add_files(self, filenames):
        storage = get_storage('output')
        rows = list()
        
        for temp_filename, filename in filenames:
            file_handle = open(temp_filename, 'rb')
            uuid = storage.store(file_handle)
            
            rows.append(dict(eventtrack_id = self.eventtrack_id,
                            file_uuid = uuid,
                            filename = filename))
            
            file_handle.close()
            os.unlink(temp_filename)
        
        if rows:
            i = EventOutputFile.__table__.insert()
            i._set_bind(DBSession.bind)
            conn = DBSession.bind.connect()
            i.execute(rows)
            DBSession.flush()
            
            session_commit(DBSession)
            
            output_files = list(DBSession.query(EventOutputFile)\
                       .filter(EventOutputFile.eventtrack_id == self.eventtrack_id))
            
            event = self.get_eventtrack()
            [event.output_files.append(o) for o in output_files]
            DBSession.add(event)
            DBSession.flush()
            self.output_files = output_files
            session_commit(DBSession)
        
    def success(self, files):
        self.add_files(files)
        session_commit(DBSession)
        self.set_end_date()

        if len(files) <= 10:
            msg = u"Success with files %s" % repr(
                    [filename for tmpfilename, filename in files])

        else:
            msg = u"Success with %s files" % len(files)

        self.info(msg, message_type="success")

        self.emit_event('finished', 'success')
        self.emit_event('success', list(DBSession.query(EventOutputFile)\
                                        .filter(EventOutputFile.eventtrack_id \
                                           == self.eventtrack_id)))
        if not self.has_postprocess:
            self.set_status('success')
            session_commit(DBSession)
        else:
            self.set_status('postprocess')
            session_commit(DBSession)
            self.post_process()
        
    def failure(self, error, failure_type="failure"):
        self.set_end_date()
        self.info('Failure with error "%s"' % str(error), message_type="failure")
        self.set_status(failure_type)
        session_commit(DBSession)
        self.emit_event(failure_type, error)
        self.emit_event('finished', failure_type)
        
    @property
    def has_postprocess(self):
        eventtrack = self.get_eventtrack()
        tube = eventtrack.tube
        return tube.has_postprocess
    
    def get_post_process_info(self):
        # TODO: reimplement that for event sets
        yield self.get_eventtrack()
       
    def post_process(self):
        self.info('Launching post-process')
        eventtrack = self.get_eventtrack()
        variant = eventtrack.variant_name
        tube = eventtrack.tube
        try:
            tube.launch_post_process(self.get_post_process_info(),
                                     variant=variant,
                                     message_callback=create_function(
                                            self.info,
                                            caller_args_count=1,
                                            kwargs=dict(source='postprocess')))
        except Exception, e:
            logger.exception(e)
            self.failure(e, failure_type="postprocess-failure")
            
        self.set_status('success')
        self.emit_event('postprocess-finished', 'success')
