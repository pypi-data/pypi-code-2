#!/usr/bin/python2

''' Locking manager
'''

import fcntl
import os

from etc import config

OP_CREATE = 'create'
OP_UPDATE = 'update'
OP_DELETE = 'delete'

class GLLock:
    ''' Locking manager with sycn integrated '''
    def __init__(self, filename):
        self.filename = filename
        self.locked = False
        self.lock_fd = None
        self.is_created = False
        self.op_type = None
        self.description = ''

    def _get_lock_fd(self):
        ''' Return the fd of the lock file '''
        if not self.lock_fd or self.lock_fd.closed:
            if not os.path.exists(self.filename):
                self.is_created = True
            self.lock_fd = open(self.filename, 'a')
        return self.lock_fd

    def _sync(self):
        ''' Commit and push to remote repository '''
        cwd = os.getcwd()
        try:
            os.chdir(config.GITOLITE_ADMIN_REPO_PATH)
        except OSError:
            os.chdir(cwd)
            return False
        # Generate commands
        stage_cmd = ''
        if self.op_type == OP_CREATE or self.op_type == OP_UPDATE:
            stage_cmd = 'git add %s &> /dev/null' % self.filename
        elif self.op_type == OP_DELETE:
            stage_cmd = '' # 'git rm %s' % self.filename
        else:
            raise RuntimeError('Given op_type invalid when locking.')
        commit_cmd = 'git commit -am "%s" &> /dev/null' % self.description
        push_cmd = 'git push origin master &> /dev/null'
        # Execute
        if (os.system(stage_cmd) == 0 and
            os.system(commit_cmd) == 0):
            # for count in range(10):
            #     if os.system(push_cmd) == 0:
            #         break
            os.chdir(cwd)
            return True
        else:
            os.chdir(cwd)
            return False

    def _fallback(self):
        ''' Revert the file. '''
        os.system('git diff %s > %s.diff' % (self.filename, self.filename))
        os.system('patch -R %s < %s.diff' % (self.filename, self.filename))
        os.remove('%s.diff' % self.filename)

    def lock(self, op_type, description='No description'):
        ''' Lock with description '''
        if self.locked:
            return True
        self.op_type = op_type
        try:
            fcntl.flock(self._get_lock_fd(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.description = description
            self.locked = True
        except IOError:
            return False
        return True

    def unlock(self, sync=True, fallback=False):
        ''' Sync if needed and unlock '''
        if not self.locked:
            return True
        if fallback:
            self._fallback()
        if sync:
            sync_result = self._sync()
        fcntl.flock(self._get_lock_fd(), fcntl.LOCK_UN)
        self._get_lock_fd().close()
        self.locked = False
        if (self.is_created and
            os.path.exists(self.filename) and
            os.fstat(self._get_lock_fd().fileno()).st_size == 0):
            # Created by locker but not changed
            os.remove(self.filename)
        if sync:
            return sync_result
        elif fallback:
            return False
        else:
            return True
