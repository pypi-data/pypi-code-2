from pyf.services.model import DBSession, Tube, session_commit
from pyf.services.core.events import create_event_track, get_logger

from pyjon.descriptors import Descriptor
import datetime

from pyf.componentized import ET
    
from pyjon.events import EventDispatcher
from pyjon.utils.main import create_function

import logging
logger = logging.getLogger() 

class Router(object):
    """ A router for a particular event group.
    
    Example initialization:
    Router(on_success = my_success_function, # should get one arg, the process that failed
           on_failure = my_failure_function) # should get two args, the process that failed and the error
    
    >>> my_router = Router()
    >>> isinstance(my_router, Router)
    True
    
    my_router.transform_and_route_flow('ageed_balance_ledger',
                                       data_stream)
    """
    
    __metaclass__ = EventDispatcher
    
    def __init__(self, dispatch=None, tube=None):
        self.dispatch = dispatch
        self.tube = tube
    
    def get_tube(self):
        if self.dispatch is not None:
            return DBSession.merge(self.dispatch).tube
        elif self.tube is not None:
            return DBSession.merge(self.tube)
        else:
            return None
    
    def update_run_date(self, variant_name=None):
        tube = self.get_tube()
        
        if variant_name is None:
            tube.last_run_date = datetime.datetime.now()
            DBSession.add(tube)
        else:
            variants = tube.get_ordered_layers(variant=variant_name)
            for variant in variants:
                variant.last_run_date = datetime.datetime.now()
                DBSession.add(variant)
                
        DBSession.flush()
        session_commit(DBSession)
        
    def process_using_dispatch(self, doc_file, variant=None, encoding=None,
                               options=None):
        dispatch = DBSession.merge(self.dispatch)
        try:
            returns = dispatch.process_file(doc_file,
                      progression_callback=create_function(self.emit_event,
                                                    before_args=['progress'],
                                                    caller_args_count=1),
                      message_callback=create_function(self.emit_event,
                                                       before_args=['info'],
                                                       caller_args_count=1),
                                            variant=variant,
                                            encoding=encoding,
                                            options=options)
            self.emit_event('success', returns)
            self.update_run_date(variant_name=variant)
        except Exception, e:
            logger.exception(e)
            self.emit_event('failure', e)
        
    def process_tube(self, variant=None,
                     options=None, source=None,
                     raises_error=False):
        tube = DBSession.merge(self.tube)
        try:
            returns = tube.flow(
                      variant=variant,
                      progression_callback=create_function(self.emit_event,
                                                    before_args=['progress'],
                                                    caller_args_count=1),
                      message_callback=create_function(self.emit_event,
                                                       before_args=['info'],
                                                       caller_args_count=1),
                      options=options,
                      source=source)
            
            self.emit_event('success', returns)
            self.update_run_date(variant_name=variant)
        except Exception, e:
            logger.exception(e)
            self.emit_event('failure', e)
    
#    def transform_and_route_flow(self,
#                                 tube_name,
#                                 data_stream,
#                                 descriptor_object=None,
#                                 descriptor_string=None,
#                                 descriptor_encoding="UTF-8",
#                                 descriptor_buffersize=16384):
#        
#        if not descriptor_object | descriptor_string:
#            raise ValueError, "Please provide a descriptor to read data"
#        
#        if descriptor_string and not descriptor_object:
#            descriptor_object = Descriptor(ET.fromstring(descriptor_string),
#                                           descriptor_encoding,
#                                           buffersize=descriptor_buffersize)
#        
#        tube = DBSession.query(Tube).filter(Tube.name == tube_name).one()
#        try:
#            tube.flow(descriptor_object, data_stream,
#                      progression_callback=self.progress,
#                      message_callback=self.message_callback)
#            self.on_success(tube_name)
#        except Exception, e:
#            self.on_failure(tube_name, e)
