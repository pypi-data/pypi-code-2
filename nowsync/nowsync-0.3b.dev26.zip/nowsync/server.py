import os
import sys
import logging
import subprocess

from werkzeug.serving import run_simple

from nowsync import core, signals, middlewares
 
def load_app(app_path):
    """Load wsgi app by path
    
    """
    module_path, app_path = app_path.split(':', 1)
    module = __import__(module_path)
    parts = module_path.split('.')
    for name in parts[1:]:
        module = getattr(module, name)
    parts = app_path.split('.')
    o = module
    for name in parts:
        o = getattr(o, name)
    return o

class AppServer(object):
    """Server for running target wsgi application
    
    """
    def __init__(self, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
            
    def run(self):
        debug = core.app.nowsync_cfg.get('debug', False)
        cfg = core.app.nowsync_cfg['app']
        wsgi_app = load_app(cfg['app_path'])
        if cfg.get('under_proxy', False):
            wsgi_app = middlewares.ReverseProxied(wsgi_app) 
        if cfg.get('user_only', True):
            wsgi_app = middlewares.AuthenMiddleware(wsgi_app, 
                core.app.nowsync_cfg['users'])
        run_simple(cfg['interface'], cfg['port'],
                   wsgi_app,
                   use_reloader=False, 
                   use_debugger=debug)

class NowSyncServer(object):
    """Server for running NowSync service
    
    """
    def __init__(self, logger=None):
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger(__name__)
        # subprocess
        self.proc = None
        
    def _stop_app(self):
        if self.proc is not None:
            self.logger.info('Stoping process %s ...', self.proc)
            if self.proc.returncode is None:
                self.proc.kill()
                self.proc.wait()
            self.logger.info('Process %s is stopped', self.proc)
            self.proc = None
            
    def _start_app(self):
        """Restart target application
        
        """
        assert self.proc is None
        self.logger.debug('Starting new process ...')
        environ = os.environ.copy()
        self.proc = subprocess.Popen([
            sys.executable,
            __file__
        ], env=environ)
        self.logger.info('Start new process')
        
    def _on_need_restart(self, sender):
        """Called when the guest application needs restart
        
        """
        self._stop_app()
        self._start_app()

    def run(self):
        """Run NowSync server
        
        """
        signals.need_restart_app.connect(self._on_need_restart)
        core.load_deps()
        debug = core.app.nowsync_cfg.get('debug', False)
        cfg = core.app.nowsync_cfg['nowsync']
        wsgi_app = core.app.wsgi_app
        if cfg.get('under_proxy', False):
            wsgi_app = middlewares.ReverseProxied(wsgi_app) 
        if cfg.get('user_only', True):
            wsgi_app = middlewares.AuthenMiddleware(wsgi_app, 
                core.app.nowsync_cfg['users'])
        self._start_app()
        try:
            run_simple(cfg['interface'], cfg['port'],
                       wsgi_app,
                       use_reloader=False, 
                       use_debugger=debug)
        except KeyboardInterrupt:
            pass
        self.logger.info('Stop NowSync server')
        
if __name__ == '__main__':
    # Notice: this is not code fore testing, the NowSyncServer will create
    # a subprocess which runs this module
    server = AppServer()
    server.run()