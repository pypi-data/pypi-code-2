#!/usr/bin/python2

''' Gitolite public key manager
'''

import os
import re

from etc import config
from gllock import GLLock

REGEXP_SET = {
    'valid_name':r'^\w+@\w+(?:\.\w+)+(?:@\w+)?$',
    'valid_public_key':r'^(?:ssh-rsa|ssh-dss) \S+ \S+$',
    }

class GLKey:
    ''' Gitolite public key manager '''
    def __init__(self, name, content=''):
        self.filename = os.path.join(config.GITOLITE_ADMIN_REPO_PATH,
                                     'keydir',
                                     name + '.pub')
        self.locker = GLLock(self.filename)
        self.name = name
        self.content = content
        self.check_parameters()

    def check_parameters(self):
        ''' Checks if parameters are valid '''
        if not (isinstance(self.name, (str, unicode)) and
                isinstance(self.content, (str, unicode))):
            raise TypeError('Parameters type invalid.')
        if not (re.match(REGEXP_SET['valid_name'], self.name) != None):
            raise ValueError('User name is not valid.')
        if (self.content and
            re.match(REGEXP_SET['valid_public_key'],
                     self.content) == None):
            raise ValueError('Public key is invalid.')
        if self.exists():
            if not (os.access(self.filename, os.R_OK) and
                    os.access(self.filename, os.W_OK)):
                raise RuntimeError('Permission denied for file %s'
                                   % self.filename)
        else:
            if not os.access(os.path.dirname(self.filename), os.W_OK):
                raise RuntimeError('Permission denied for directory %s'
                                   % os.path.dirname(self.filename))

    def get_id(self):
        ''' ID '''
        return self.name

    @staticmethod
    def index():
        ''' List all key names '''
        dirpath = os.path.join(config.GITOLITE_ADMIN_REPO_PATH, 'keydir')
        if not os.access(dirpath, os.R_OK):
            raise RuntimeError('Permission denied for directory %s'
                               % os.path.dirname(dirpath))
        key_list = filter(lambda x: x.endswith('.pub'),
                          os.listdir(dirpath))
        key_list = [x[:-4] for x in key_list]
        return key_list
    
    def exists(self):
        ''' Check if the key exists '''
        return (os.path.exists(self.filename) and
                (not self.locker.locked or not self.locker.is_created))

    def update(self, content):
        ''' Create a new public key '''
        assert self.locker.locked
        # Write content
        try:
            fdw = open(self.filename + '.tmp', 'w')
            fdw.write(content)
            fdw.close()
            os.rename(self.filename + '.tmp', self.filename)
            self.content = content
        except Exception:
            raise RuntimeError('Error when writing file %s' % self.filename)
        return True

    def create(self):
        ''' Update the specific public key file '''
        assert self.locker.locked
        if not self.content:
            raise ValueError('Public key can not be empty.')
        if not self.exists():
            if self.update(self.content):
                return self.get_id()
        else:
            raise RuntimeError('File %s already exists.' % self.filename)

    def delete(self):
        ''' Delete the public key with name and value '''
        assert self.locker.locked
        if not os.path.exists(self.filename):
            raise RuntimeError('File %s not exists when deleting'
                               % self.filename)
        try:
            os.remove(self.filename)
        except Exception:
            raise RuntimeError('Error when removing file %s' % self.filename)
        return True

    def get_content(self):
        ''' Return the content of the key '''
        if self.content:
            return self.content
        if self.exists():
            fdr = open(self.filename, 'r')
            self.content = fdr.read()
            fdr.close()
            return self.content
        else:
            raise RuntimeError('Error when reading file %s' % self.filename)

    def to_dict(self):
        ''' Convert to dict '''
        return dict(name=self.name,
                    pubkey=self.get_content())

    def lock(self, description='No description'):
        ''' Dispatch to GLLock '''
        return self.locker.lock(description)

    def unlock(self, sync=True):
        ''' Dispatch to GLLock '''
        return self.locker.unlock(sync)
