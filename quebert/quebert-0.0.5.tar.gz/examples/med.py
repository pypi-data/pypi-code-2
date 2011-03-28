try:
    import json
except ImportError:
    import simplejson as json

import time
import socket
import urllib

from datetime import datetime, timedelta

from twisted.internet import reactor, defer
from twisted.web import client
from twisted.python import log

from quebert import amqp, mediator
from quebert import common as qc

def timedeltaToSeconds(td):
    return td.days*24*60*60+td.seconds

fqdn = socket.getfqdn()

class DelayOnErrorWatcher(amqp.Watcher):
    """
    I'm a more clever mediator that through the use of the except hook
    achieves exponential backoff on task failure. To keep track of
    failures I append metadata on the task itself.
    """
    def __init__(self, *args, **kwargs):
        self.constant = kwargs.pop('constant', 1.5)
        self.maxDelay = kwargs.pop('maxDelay', 120)
        self.delayThreshold = kwargs.pop('delayThreshold', 60)

        super(DelayOnErrorWatcher, self).__init__(*args, **kwargs)

    def exceptionHandler(self, reason, task):
        d = defer.Deferred()
        if 'failures' in task:
            failures = task['failures'] = task['failures'] + 1
        else:
            failures = task['failures'] = 1
        task['traceback'] = unicode(reason)

        nextDelay = min(self.constant**failures, self.maxDelay)
        self.reactor.callLater(nextDelay, d.callback, task)

        # Now if the delay is big enough, increase the prefetch
        # and remember to remove it when coming back.
        def decreasePrefetch(content):
            self.decreaseEvents()
            return content

        if nextDelay > self.delayThreshold:
            self.increaseEvents()
            d.addCallback(decreasePrefetch)
        return d

    def runAtHook(self, task):
        if 'run_at' in task:
            runAt = qc.parse_date(task['run_at'])
            now = qc.now()

            if runAt > now:
                delay = timedeltaToSeconds(runAt-now)
                log.msg("delaying until %s, for %s" % (runAt, delay))

                d = defer.Deferred()
                self.reactor.callLater(delay, d.callback, None)

                self.increaseEvents()
                d.addCallback(lambda _: self.decreaseEvents())
                return d

        log.msg("I'm about to execute this %s" % (task,))

def main(options=None):
    """
    Use me either directly or by going through:

    twistd -no quebert --config=med.main
    """
    username = "guest"
    password = "guest"
    host = "localhost"
    exchange = "flow"

    def postProcess(task, result):
        log.msg("Result for task %s is %s" % (task, result))

    def onConnectionError(e):
        log.err(e)

    client = amqp.TxAMQPClient(host, username, password,
                               watcherFactory=DelayOnErrorWatcher)

    bindings = [(exchange, "high-priority-queue", "tasks.high"),
                (exchange, "medium-priority-queue", "tasks.medium"),
                (exchange, "low-priority-queue", "tasks.low")]

    @defer.inlineCallbacks
    def _run():
        for d in map(lambda a: client.watch(*a), bindings):
            try:
                watcher = yield d
            except Exception, e:
                log.err(e)

            m = mediator.Mediator()
            m.addPrehook(watcher.runAtHook)
            m.addPosthook(postProcess)

            watcher.loop(m, 120, 5, onConnectionError)

    _run()

if __name__ == "__main__":
    import sys
    log.startLogging(sys.stdout)
    reactor.callLater(0, main)
    reactor.run()
