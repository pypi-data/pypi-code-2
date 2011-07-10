
import logging
import os
import pyinotify
import signal

from threading import Timer

class OnWriteHandler(pyinotify.ProcessEvent):

    def my_init(self, pidfile, log):
        self.log = log
        self.sig = signal.SIGHUP
        self.pidfile = pidfile
        self.pid = None
        self.interval = 2.0
        self.timer = None
        self.extensions = [".py", ".ini"]
        log.debug("Created Watcher")

    def process_IN_CREATE(self, event):
        self.process_IN_MODIFY(event)

    def process_IN_DELETE(self, event):
        self.process_IN_MODIFY(event)

    def process_IN_MODIFY(self, event):
        if self.timer:
            self.log.info("%s changed, delaying reload", event.pathname)
            self.timer.cancel()
        else:
            self.log.info("%s changed, reloading in %d sec",
                          event.pathname, self.interval)

        self.timer = Timer(self.interval, reload_uwsgi,
                           [self.log, event, self.pidfile, self.sig])
        self.timer.start()


def reload_uwsgi(log, event, pidfile, sig):
    try:
        with open(pidfile, 'r') as f:
            pid = int(f.read().strip())
    except:
        log.exception("Cannot read pidfile, reloading aborted")
        return

    os.kill(pid, sig)
    log.debug("Killing pid %s with signal %s", pid, sig)
    log.warn("=" * 20 + " RELOADING uWSGI " + "=" * 20)


def quick_check(notifier):
    assert notifier._timeout is not None, \
            'Notifier must be constructed with a short timeout'
    while notifier.check_events():
        notifier.read_events()
        notifier.process_events()


def filter_path(pathname):
    extensions = (".py", ".ini")
    if all(not pathname.endswith(ext) for ext in extensions):
        return False
    return True


def watch(paths, pidfile):
    logger = logging.getLogger(__name__)
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler(pidfile=pidfile, log=logger)
    notifier = pyinotify.Notifier(wm, handler, timeout=10)
    for path in paths:
        logger.info("Starting file watcher on path %s", path)
        wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True, auto_add=True,
                     exclude_filter=filter_path)
    return notifier


if __name__ == '__main__':

    def fakereload(self, event):
        print "%s changed" % (event.pathname)

    paths = ["/tmp"]
    OnWriteHandler.reload = fakereload

    logging.basicConfig(level=logging.DEBUG)
    notifier = watch(paths)
    notifier.loop()
