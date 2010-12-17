#!/usr/bin/env python
'''
sweety.util

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''

import datetime
import getpass
import os
import random
import shutil
import sys
#import traceback
os_name = os.name
if os_name == 'posix':
    import fcntl

def column_name2index(columns, header):
    newcols = []
    for column in columns:
        try:
            newcols.append(int(column))
        except:
            newcols.append(header.index(column))
    return newcols

def get_lock_tmpfile(lockname):
    if os_name == 'posix':
        return '/tmp/%s.user=%s.pid=%d.gid=%d.lock' % (lockname,
                                                       getpass.getuser(),
                                                       os.getpid(),
                                                       os.getgid())
    else:
        return 'c:\\%s.user=%s.pid=%d.lock' % (lockname,
                                                       getpass.getuser(),
                                                       os.getpid())


class FileLock(object):
    def __init__(self, name, istmp = True):
        '''
        Initializes a Lock object.
        
        @param name: the lock name.
        @param istmp: indicates the file used for locking is temporary, which should be deleted after unlocking.
        '''

        self.name = name
        self.istmp = istmp

        if not self.name:
            self.name = get_lock_tmpfile(os.path.basename(sys.argv[0]))
        else:
            if os_name == 'posix':
                if not self.name.startswith('/') and self.istmp:
                    self.name = os.path.join('/tmp', self.name)
            else:
                self.name = os.path.join('c:', self.name)

        self.fd = None

    def __del__(self):
        self.unlock()

    def lock(self):
        '''
        lock(self) -> None
        
        Acquires a lock.
        '''
        if not self.fd:
            self.fd = open(self.name, 'a')

        if os_name == 'posix':
            fcntl.lockf(self.fd, fcntl.LOCK_EX)

    def unlock(self):
        '''
        unlock(self) -> None
        
        Releases the lock.
        '''
        if not self.fd:
            return

        self.fd.close()
        self.fd = None

        if self.istmp and os.path.exists(self.name):
            os.unlink(self.name)


class Shelter(object):
    '''
    A Shelter provides process a safe environment for temporary file storage.
    '''
    def __init__(self, name):
        '''
        Initializes a new Shelter object.
        '''
        self.name = name
        self.path = os.path.join('/tmp', '%s.%d.%s_%s' % (name, os.getpid(), self.get_timestamp(), str(random.random()).split('.')[1]))

        os.makedirs(self.path)


    def __del__(self):
        '''
        Destructor
        '''
        self.depose()


    def get_timestamp(self):
        '''
        get_timestamp(self) -> string
        
        Gets current time stamp.
        
        @return: string of time stamp.
        '''
        n = datetime.datetime.now()

        return '%s.%s' % (n.strftime('%Y-%m-%d_%T'), n.microsecond)


    def get_unique_filename(self, filename):
        '''
        get_unique_filename(self, filename) -> string
        
        Gets a unique filename inside the sheltered environment.
        
        @param filename: the base part of the filename.
        @return: a string of full filename.
        '''
        return os.path.join(self.path, '%s.%s' % (filename, self.get_timestamp()))


    def get_filename(self, filename):
        '''
        get_filename(self, filename) -> string
        
        Gets a filename inside the sheltered environment.
        
        @param filename: the base part of the filename.
        @return: a string of full filename.
        '''
        return os.path.join(self.path, filename)


    def depose(self):
        '''
        depose(self) -> None
        
        Deposes the sheltered environment.
        '''
        if os.path.isdir(self.path):
            shutil.rmtree(self.path)


