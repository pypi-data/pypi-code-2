# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist
from __future__ import with_statement

from threading import Lock

# TODO: this should be the versioning module

class Scheduler(object):

    def __init__(self):
        self.__graphs = {}
        self.__write_lock = Lock()
        self.__workers = []
    
    def schedule_operation(self, graph_id, operation):
        """
        Schedules an operation to a worker.
        
        ``graph_id`` - the id of the graph the operation is execution on
        ``operation`` - a hash-map containing:
            ``type``, operation type is either 'create', 'add', 'update',       
                      'remove', ...
            ``data``, absolute path to the temporary file with request content
            ``username``, string with username of the user exec. the request
            ``ttl``, defines the ttl of the graph
        """
    
        # no other thread can schedule operations at the same time
        with self.__write_lock:
            try:
                (worker, version) = self.__graphs[graph_id]
            except KeyError, e:
                # round-robin select worker, take the first and place it last
                worker = self.__workers.pop(0)
                self.__workers.append(worker)
                version = 1
            
            # store the new version and worker for the graph and unlock
            # making this critical section non-blocking. 
            self.__graphs[graph_id] = (worker, version+1)

        # Thread blocks for response while sending the operation to the worker
        # Concurrent operations can be sent to a worker. If they are to the
        # same graph, the worker will order them according to the version number
