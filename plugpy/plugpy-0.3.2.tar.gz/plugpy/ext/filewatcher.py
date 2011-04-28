from plugpy import Plugin, log, abspath
import os
import os.path
import fnmatch 
import thread
import time

default_ignore = ['*/.git', '*/.git/*', '*/.hg', '*/.hg/*', '*/.svn/*', '*/.svn', '*/CVS/*', '*.pyc']
default_ext = ['.py']
default_interval = '1'
default_files = ["./"]


class FileWatchPlugin(object):
    
    _ignore = []
    running = False

    def __init__(self, **config):
        self.setup(**config)

    def setup(self, **config):
        self.files = {}
        
        observe_ext = config.get('observe_ext', default_ext)
        if not type(observe_ext) is list:
            observe_ext = [observe_ext]
        self._observe_ext = observe_ext
        log('observe_ext %s' % self._observe_ext)

        self._interval = int(config.get('interval', default_interval))
        log('interval %s' % self._interval)
        
        self._ignore = default_ignore
        self._ignore.extend(config.get('ignore', []))
        log('ignore %s' % self._ignore)
        
        observe_file = config.get('observe_files', default_files)
        if not type(observe_file) is list:
            observe_file = [observe_file]

        observe_file = map(abspath, observe_file)
        log('observe_files %s' % observe_file)
        self.observe(observe_file)
        
    def on_start(self, use_thread=False):
        if use_thread:
            thread.start_new_thread(self.run, ())
        else:
            self.run()

    def run(self):
        if self.running:
            return

        self.running = True
        while self.running:
            self.check()
            time.sleep(self._interval)

    def observe(self, files):
        for file in files:
            file = file.strip()
            if os.path.isdir(file):
                if not self.ignore_filter(file):
                    self.save_mtime(file)
                
                self.dir_observe(file)
            else:
                path = os.path.abspath(file)
                if not self.ignore_filter(path):
                    self.save_mtime(path)
        log('find files %s' % self.files.keys())

    def dir_observe(self, dir):

        created = []
        for root, dirs, files in os.walk(dir):
            for file in files:
                path = os.path.join(root, file)
                if not self.ignore_filter(path):
                    newfile = self.save_mtime(path)
                    if newfile:
                        created.append(newfile)
            for dir in dirs:
                path = os.path.join(root, dir)
                if not self.ignore_filter(path):
                    newfile = self.save_mtime(path)
                    if newfile:
                        created.append(newfile)
        return created
                
    def save_mtime(self, path, force=False):
        if os.path.exists(path):
            match = False
            if not os.path.isdir(path):
                for ext in self._observe_ext:
                    if path.endswith(ext.strip()):
                        match = True
                        break
                if not match:
                    return 
            if force or not path in self.files:
                self.files[path] = os.stat(path).st_mtime
                return path
    
    def check(self):
        created = []
        modified = []
        deleted = []
        for path, mtime in self.files.items():
            c, m, d = self.is_modify(path, mtime)
            created.extend(c)
            modified.extend(m)
            deleted.extend(d)

        if created or modified or deleted:
            log('modify files created %s modified %s deleted %s' % (created,
                modified, deleted))
            self.on_modified(created=created, modified=modified,
                    deleted=deleted)
    
    def on_modified(self, created, modified, deleted):
        pass
    
    def is_modify(self, path, mtime):

        created = []
        modified = []
        deleted = []
        if not os.path.exists(path):
            del self.files[path]
            deleted.append(path)
        else:
            if os.stat(path).st_mtime > mtime:
                self.save_mtime(path, True)
                if os.path.isdir(path):
                    created.extend(self.dir_observe(path))
                else:
                    modified.append(path)

        return created, modified, deleted
    
    def ignore_filter(self, path):
        return reduce(lambda x,y:x or y,
                [fnmatch.fnmatch(path, i) for i in self._ignore])
    
    def on_stop(self):
        self.running = False

