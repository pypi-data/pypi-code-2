from plugpy import Plugin, log
import os
import sys
import thread

environ_key = 'RUN_AUTO_RELOAD_PLUGIN'

def use_autoreload():
    return os.environ.get(environ_key) == "true"

def restart_with_reloader():
    while True:
        args = [sys.executable] + sys.argv
        if sys.platform == "win32":
            args = ['"%s"' % arg for arg in args]
        new_environ = os.environ.copy()
        new_environ[environ_key] = 'true'
        exit_code = os.spawnve(os.P_WAIT, sys.executable, args, new_environ)
        if exit_code != 3:
            return exit_code


class AutoReloadPlugin(object):
    
    require_reload = False
    
    def reloader_run(self, main_loop, reloader_loop):
        if use_autoreload():
            
            thread.start_new_thread(reloader_loop, ())
            try:
                main_loop()
            except KeyboardInterrupt:
                if self.require_reload:
                    sys.exit(3)
        else:
            try:
                sys.exit(restart_with_reloader())
            except KeyboardInterrupt:
                pass
    
    def on_start(self):
        log("start auto reloader")
        self.reloader_run(self.main_loop, self.reloader_loop)

    def main_loop(self):
        pass

    def reloader_loop(self):
        pass

    def on_reload(self):
        log("reload")
        self.require_reload = True
        thread.interrupt_main()

    def on_stop(self):
        log("stop")
        thread.interrupt_main()
    


