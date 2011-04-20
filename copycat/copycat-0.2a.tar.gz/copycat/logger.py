'''
Created on Apr 17, 2009

@author: felipe
'''

import os
import pickle
import fileutils as fu

from cPickle import Pickler

class Logger():
    def __init__(self, basedir):
        self.basedir = basedir
        
        last_file_name = fu.last_log_file(basedir)
        
        if last_file_name and os.path.getsize(basedir + last_file_name) < fu.MAX_LOGFILE_SIZE:
            self.file = fu.RotateFileWrapper(open(basedir + last_file_name,'ab'), basedir)
        else:
            self.file = fu.RotateFileWrapper(open(fu.next_log_file(basedir),'wb'), basedir)
        
        self.pickler = Pickler(self.file, pickle.HIGHEST_PROTOCOL)

        self.file.set_pickler(self.pickler)
        
    '''
        Subscriber interface
    '''
    def receive(self, message):
        self.pickler.dump(message)
        
    def close(self):
        if not self.file.closed:
            self.file.close()
