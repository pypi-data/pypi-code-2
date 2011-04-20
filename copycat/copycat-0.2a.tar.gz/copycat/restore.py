'''
Created on Apr 17, 2009

@author: felipe
'''

import os
import logging
import fileutils as fu

from snapshot import SnapshotManager
from datetime import datetime
from datetime import timedelta
from cPickle import Unpickler

l = logging.getLogger("copycat")
LOG_PREFIX = '[RESTORE] '

class RestoreHelper():
        
    @staticmethod
    def restore(system, basedir, clock):
        
        system = SnapshotManager(basedir).recover_snapshot()
        
        files = fu.last_log_files(basedir)
        l.debug(LOG_PREFIX + "Files found: " + str(files))
        if not files:
            return system
        
        actions = []
        for file in files:
            l.debug(LOG_PREFIX + "Opening  " + str(file))
            unpickler = Unpickler(open(file,'rb'))
            try:
                while True:
                    action = unpickler.load()
                    l.debug(LOG_PREFIX + action.action)
                    actions.append(action)
            except EOFError:
                pass
                
        if not actions:
            return system
        
        l.debug(LOG_PREFIX + "Actions re-execution")
        for action in actions:
            try:
                action.execute_action(system)
            except Exception as e:
                l.debug(LOG_PREFIX + 'Error executing :' + str(action))
            
        clock.reset()
            
        return system
        
