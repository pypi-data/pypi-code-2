from django.core.management.base import CommandError
from django.conf import settings
import os
import signal
import sys
import time
import subprocess

class RunOnce(object):
    def __init__(self, attrname):
        self.attrname = attrname
    def __call__(self, f):
        attrname = self.attrname
        def w(self, *args, **kwargs):
            if not hasattr(self, attrname):
                setattr(self, attrname, f(self, *args, **kwargs))
            return getattr(self, attrname)                
        return w
        
class Backend(object):
    def __init__(self, name, graceful):
        self.name = name
        self.graceful = graceful
        self.socket = os.path.join(self.graceful.statedir, "fastcgi-%s.socket" % self.name)
        self.pidfile = os.path.join(self.graceful.statedir, "fastcgi-%s.pid" % self.name)
    
    def is_up(self):
        if os.path.exists(self.pidfile):
            try:
                f = open(self.pidfile, 'r')
                pid = int(f.read())
                f.close()
            except (IOError, ValueError):
                return False
            try:
                os.kill(pid, 0)
                return pid
            except OSError:
                return False
        else:
            return False
            
    def is_active(self):
        try:
            return os.readlink(self.graceful.socket) == self.socket
        except OSError:
            return False
            
    def __repr__(self):
        return "[%s] backend %s (%s)" % (
                '*' if self.is_active() else ' ',
                self.name,
                'running' if self.is_up() else 'down',
            )
            
    def start(self):
        if self.is_up():
            print 'Skipping already running backend "%s"' % self.name
            return
        options = getattr(settings, 'GRACEFUL_OPTIONS', {})
        if type(options) == dict:
            options.update({'socket': self.socket, 'pidfile': self.pidfile, 'daemonize': 'true'})
        else:
            raise CommandError('GRACEFUL_OPTIONS optional setting should be set to a dictionary of options to runfcgi command.')
        subprocess.Popen([sys.executable, sys.argv[0], 'runfcgi'] + ['%s=%s' % (k, options[k]) for k in options]).wait()
        if not self.is_up():
            raise CommandError('Backend "%s" failed to start.' % self.name)
        while not os.path.exists(self.socket):
            time.sleep(0.1)
        print 'Started backend "%s".' % self.name
        try:
            os.chmod(self.socket, 0666)
        except Exception, e:
            print "chmod 666 %s failed" % self.socket
        
    def stop(self):
        pid = self.is_up()
        if not pid:
            print 'Skipping stopped backend "%s"' % self.name
            return
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception, e:
            print "unable to kill %d: %s" % (pid, e)
        for filename in (self.socket, self.pidfile):
            try:
                os.unlink(filename)
            except:
                pass
        print 'Stopped backend "%s".' % self.name
        
    def switch(self):
        if os.path.exists(self.graceful.socket) or os.path.islink(self.graceful.socket):
            os.unlink(self.graceful.socket)
        os.symlink(self.socket, self.graceful.socket)
        print 'Switched to backend "%s".' % self.name
            
class Graceful(object):
    def __init__(self):
        try:
            self.statedir = settings.GRACEFUL_STATEDIR
        except AttributeError:
            raise CommandError('GRACEFUL_STATEDIR setting is required for this command to work.')
        if not os.path.isdir(self.statedir):
            raise CommandError('Path "%s" specified in GRACEFUL_STATEDIR setting should be a writable directory.' % self.statedir)            
        self.socket = os.path.join(self.statedir, "fastcgi.socket")
        self.backends = (
                Backend('a', graceful=self),
                Backend('b', graceful=self),
            )
        self.map = dict([(b.name, b) for b in self.backends])
