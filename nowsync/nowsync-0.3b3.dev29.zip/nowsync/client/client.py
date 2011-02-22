from __future__ import with_statement
import sys
import os
import logging
import time
import urllib
import hashlib

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from nowsync.client import api
from nowsync.models.file import is_under_dir, get_files, match_patterns
from nowsync.utils import relpath

class NowSyncClient(FileSystemEventHandler):
    """Sync client for monitoring file change and communicates with server
    
    """
    
    def __init__(self, config, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        self.config = config
        self.url = config['client']['url']
        self.sync_path = os.path.realpath(config['sync_path'])
        
        username = config['client']['username']
        password = config['client']['password']
        self.api = api.SyncAPI(self.url, username, password)
        self.ignorefiles = config['ignore_files']
        self.syncfiles = config['sync_files']
            
    def _need_sync(self, path):
        """Determine does a file need sync
        
        """
        rel = relpath(path, self.sync_path)
        if match_patterns(rel , self.ignorefiles):
            return False
        if match_patterns(rel , self.syncfiles):
            return True
        return False
        
    def _to_remote_path(self, path):
        """Convert local path to remote path
        
        """
        rel = relpath(path, self.sync_path)
        remote_path = urllib.pathname2url(rel.encode('utf8'))
        return remote_path
        
    def _put_file(self, path, skip_sig_check=False):
        """Put a local file to remote
        
        """
        remote_path = self._to_remote_path(path)
        
        if not skip_sig_check:
            # make sure the file is not same as our local one
            try:
                sig = self.api.signature(remote_path)
            except Exception:
                self.logger.error('Failed to get signature', exc_info=True)
                return False
            
        try:
            with open(path, 'rb') as file:
                content = file.read()
        except IOError:
            self.logger.error('Failed to read file %s', path, exc_info=True)
            return False
            
        if not skip_sig_check:
            local_sig = hashlib.sha1(content).hexdigest()
            if local_sig == sig:
                self.logger.info('File %s is same as local one', remote_path)
                return False
        
        try:
            self.api.put(content, remote_path)
        except Exception:
            self.logger.error('Failed to put file %s', path, exc_info=True)
            return False
        return True
    
    def _del_file(self, path):
        """Delete a remote file
        
        """
        remote_path = self._to_remote_path(path)
        try:
            self.api.delete(remote_path)
        except Exception:
            self.logger.error('Failed to delete file', exc_info=True)
            return
        
    def on_created(self, event):
        self.logger.info('File %s was created', event.src_path)
        if not self._need_sync(event.src_path):
            return
        if os.path.exists(event.src_path) and os.path.isfile(event.src_path):
            self._put_file(event.src_path)
            
    def on_modified(self, event):
        self.logger.info('File %s was modified', event.src_path)
        if not self._need_sync(event.src_path):
            return
        if os.path.exists(event.src_path) and os.path.isfile(event.src_path):
            self._put_file(event.src_path)
        
    def on_deleted(self, event):
        self.logger.info('File %s was deleted', event.src_path)
        if not self._need_sync(event.src_path):
            return
        self._del_file(event.src_path)
        
    def on_moved(self, event):
        self.logger.info('File %s was moved to %s', 
                         event.src_path, event.dest_path)
        if not self._need_sync(event.src_path):
            return
        # del src file
        if is_under_dir(event.src_path, self.sync_path):
            self._del_file(event.src_path)

    def resync(self):
        """Resync all files
        
        """
        self.logger.debug('Resyncing all files ...')
        remote_files = self.api.files()
        local_files = get_files(self.sync_path, self.syncfiles, 
                                self.ignorefiles)
        for path, sig in remote_files.iteritems():
            local_path = urllib.url2pathname(path)
            # we don't have
            if path not in local_files:
                self.logger.debug('Remote %s does not exist in local', path)
            else:
                local_sig = local_files[path]
                # different, push
                if sig != local_sig:
                    self.logger.debug('Remote %s is different from local', 
                                      path)
                    self._put_file(local_path, skip_sig_check=True)
        
        for path in local_files:
            # they don't have this one, push
            if path not in remote_files:
                self.logger.debug('Remote does not have %s', path)
                local_path = urllib.url2pathname(path)
                self._put_file(local_path, skip_sig_check=True)
        
        self.logger.info('All files are sync')

    def run(self):
        """Sync to remote server
        
        """
        self.logger.info('Sync path %s to %s', self.sync_path, self.url)
        # Notice: somehow, the kqueue observer works oddly under Mac OSX
        # thus, we use polling observer under mac
        if sys.platform == 'darwin':
            from watchdog.observers.polling import PollingObserver 
            observer = PollingObserver()
        else:
            observer = Observer()
        observer.schedule(self, path=self.sync_path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
