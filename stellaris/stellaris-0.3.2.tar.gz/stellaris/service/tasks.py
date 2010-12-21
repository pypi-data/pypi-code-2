# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import logging

from benri.app import WSGICollection, json
from benri.threadstage import EventHandler

from uuid import uuid4 as uuid

from paste.httpexceptions import HTTPMultipleChoices, HTTPSeeOther, HTTPNotFound, HTTPBadRequest, HTTPConflict, HTTPInternalServerError, HTTPMethodNotAllowed

log = logging.getLogger('stellaris')

class TaskHandler(EventHandler):

    def __init__(self, tasks):
        self.__tasks = tasks

    def event_worker_done(self, res):
        return res
        
    def event_worker_failed(self, exc):
        raise exc

class BackendGraphs(WSGICollection):

    def __init__(self, stage):
        """
        Collection of backend graphs. Makes it possible to create, delete and 
        retrieve the data in a graph. Requests to the backend graph is 
        serialized by a version.
        """
        self.__stage = stage
        WSGICollection.__init__(self, uri_prefix='/backend/graphs/')

    # POST /tasks/
    # body contains a json encoded message with the following parameters
    # 'state' - message passed to the stage
    # 'event' - type of the operation passed to the stage handler
    # 'version' - message version according to the initiator
    @json
    def create(self, env, resp):
        task_id = str(uuid())
        
        req = env['benri.json']
        
        self.__stage.send(None, req['event'], req['state'], req['version'])
        
        
