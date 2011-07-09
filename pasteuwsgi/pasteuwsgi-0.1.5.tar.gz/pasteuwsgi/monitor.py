
import logging
import os
import pyinotify
import datetime
import signal


class OnWriteHandler(pyinotify.ProcessEvent):

    def my_init(self, pid, log):
        self.log = log
        self.sig = signal.SIGHUP
        self.pid = pid
        self.extensions = [".py", ".ini"]
        self.last_event = datetime.datetime.now()
        log.debug("Created Watcher")

    def process_IN_CREATE(self, event):
        self.process_IN_MODIFY(event)

    def process_IN_DELETE(self, event):
        self.process_IN_MODIFY(event)

    def process_IN_MODIFY(self, event):
        if all(not event.pathname.endswith(ext) for ext in self.extensions):
            return
        self.reload(event)

    def reload(self, event):
        # Do not reload too fast

        now = datetime.datetime.now()
        diff = now - self.last_event
        if diff.total_seconds() > 3:
            self.last_event = now
            self.log.info("%s changed, reloading", event.pathname)
            self.log.warn("=" * 20 + " RELOADING uWSGI " + "=" * 20)
            os.kill(self.pid, self.sig)


def quick_check(notifier):
    assert notifier._timeout is not None, \
            'Notifier must be constructed with a short timeout'
    while notifier.check_events():
        notifier.read_events()
        notifier.process_events()


def watch(paths, pid):
    logger = logging.getLogger(__name__)
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler(pid=pid, log=logger)
    notifier = pyinotify.Notifier(wm, handler, timeout=10)
    for path in paths:
        logger.info("Starting file watcher on path %s", path)
        wm.add_watch(path, pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    return notifier


if __name__ == '__main__':

    def fakereload(self, event):
        print "%s changed" % (event.pathname)

    paths = ["/tmp"]
    OnWriteHandler.reload = fakereload

    logging.basicConfig(level=logging.DEBUG)
    notifier = watch(paths)
    notifier.loop()
