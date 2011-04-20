'''
Created on Apr 16, 2009

@author: felipe
'''

__author__ = "Felipe Cruz<felipecruz@loogica.net>"
__license__ = "BSD"
__version__ = "0.2"

import os
import time
import logging
import thread
import threading
import types
import sys

import fileutils as fu

from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

from logger import *
from restore import *
from replication import *
from snapshot import *
from network import *

l = None

CORE_LOG_PREFIX = '[CORE] '

def logging_config(log_file_path):
    result = logging.getLogger("copycat")
    result.setLevel(logging.DEBUG)
    
    handler = RotatingFileHandler(log_file_path, "a", 1000000, 10)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s ' \
                                 '- %(message)s', '%a, %d %b %Y %H:%M:%S')
    handler.setFormatter(formatter)
    result.addHandler(handler)
    return result

def action_check(obj):
    unlocked = False
    readonly = False
    abort_exception = False
    try:
        unlocked = obj.__unlocked
    except AttributeError:
        pass
    try:
        readonly = obj.__readonly
    except AttributeError:
        pass
    try:
        abort_exception = obj.__abort_exception
    except AttributeError:
        pass
    
    return (readonly, unlocked, abort_exception)

def init_system(obj, basedir=None, snapshot_time=0, master=False, 
                replication=False, port=5466, host='localhost', 
                password='copynet', ipc=False):

    if not basedir: 
        basedir = fu.obj_to_dir_name(obj)
    basedir = fu.name_to_dir(basedir)

    try:
        files = os.listdir(basedir)
    except os.error, e:
        os.mkdir(basedir)
        
    log_file_path = os.path.join(basedir,"copycat.log")
        
    global l
    l = logging_config(log_file_path)
    
    if not obj:
        raise Exception(CORE_LOG_PREFIX + "Must input a valid object if there's no snapshot files")
    
    if not fu.last_snapshot_file(basedir):
        l.info(CORE_LOG_PREFIX + "No snapshot files..")
        if isinstance(obj, type) or isinstance(obj, types.ClassType):
            obj = obj()
        SnapshotManager(basedir).take_snapshot(obj)
    
    start = datetime.utcnow()
    l.info(CORE_LOG_PREFIX + "Copycat init....")
    obj = RestoreHelper.restore(obj, basedir, clock)
    end = datetime.utcnow()
    delta = end - start
    l.info(CORE_LOG_PREFIX + "Spent " + str(delta) + "microseconds")
    return CopycatProxy(obj, basedir, snapshot_time, master, replication, host, password, port=port, ipc=ipc)

class CopycatProxy():
    def __init__(self, obj, basedir, snapshot_time, master, replication, host, password, port, ipc):
        self.obj = obj
        self.basedir = basedir
        self.publisher = Publisher()
        logger = Logger(basedir)
        self.publisher.register(logger)
        self.lock = threading.RLock()
        self.snapshot_manager = SnapshotManager(basedir)
        self.snapshot_timer = None
        self.replication = replication
        self.slave = None
        self.master = master
        
        if snapshot_time:
            self.snapshot_timer = SnapshotTimer(snapshot_time, self)
            time.sleep(snapshot_time)
            self.snapshot_timer.start()
        
        if master:
            self.server = CopyNet(self.obj, port=port, password=password, ipc=ipc)
            self.server.start()
            self.publisher.register(self.server)
            self.slave = None
            
        if not master and replication:
            self.server = None
            self.slave = CopyNetSlave(self.obj, self, host=host, password=password, port=port, ipc=ipc)
            self.slave.start()

    def __getattr__(self, name):
        if name[0:2] == '__'  or not callable(getattr(self.obj, name)) :
            return getattr(self.obj, name)
        
        (readonly,unlocked,abort_exception) = action_check(getattr(self.obj, name))
        
        if not readonly and (self.replication and not self.master):
            raise Exception('This is a slave/read-only instance.')
            
        def method(*args, **kwargs):
            try:
                if not unlocked:
                    self.lock.acquire(1)
                
                action = Action(thread.get_ident(), name, datetime.now(), args, kwargs)
                system = None                  
              
                try:
                    system = action.execute_action(self.obj)
                except Exception as e:
                    l.debug(CORE_LOG_PREFIX + 'Error: ' + str(e))
                    if abort_exception:
                        l.debug(CORE_LOG_PREFIX + 'Aborting action' + str(action))
                    if not abort_exception:
                        self.publisher.publish(action)
                    raise e
                
                if not readonly:
                    self.publisher.publish(action)
                
            finally:
                if not unlocked:
                    self.lock.release()
                    
            return system
        
        return method
    
    def take_snapshot(self):
        if self.slave:
            self.slave.acquire()
        self.snapshot_manager.take_snapshot(self.obj)
        if self.slave:
            self.slave.release()
    
    def close(self):
        self.publisher.close()
        logging.shutdown()
        if self.snapshot_timer:
            self.snapshot_timer.stop()
    
    def shutdown(self):
        if self.master:
            self.server.close()
        if self.slave:
            self.slave.close()

class Action():
    def __init__(self, caller_id, action, timestamp, args, kwargs):
        self.caller_id = caller_id
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.timestamp = timestamp
        
    def __str__(self):
        return "action %s \ncaller_id %s \nargs %s" % (self.action, str(self.caller_id), self.args)
    
    def execute_action(self, system):
        method = getattr(system, self.action)
        clock.set_time(self.timestamp)
        return method(*self.args, **self.kwargs)

class Clock():
    def __init__(self):
        if not '_clock' in globals():
            self.datetime = None
            self.reexecution = False
            globals()['_clock'] = self
    
    def reset(self):
        globals()['_clock'].reexecution = False
  
    def now(self):
        if not '_clock' in globals():
            return datetime.now()
        if not globals()['_clock'].datetime:
            return datetime.now()
        if not globals()['_clock'].reexecution:
            return datetime.now()
        
        return globals()['_clock'].datetime
        
    def set_time(self, datetime):
        globals()['_clock'].reexecution = True
        globals()['_clock'].datetime = datetime
        
clock = Clock()