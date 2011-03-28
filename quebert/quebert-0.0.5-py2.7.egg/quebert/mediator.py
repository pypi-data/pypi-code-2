try:
    import json
except ImportError:
    import simplejson as json

import urlparse

from datetime import timedelta

from twisted.python import log
from twisted.internet import defer, reactor
from twisted.web import client

from quebert import common as qc

class Mediator(object):
    """
    A mediator is none other than a dispatcher for tasks that are
    submitted to the queue. Once it receives a message it sends a
    request with the passed arguments using the given url (that is now
    the task identifier).

    This class is mostly amqp ignorant and only needs to receive
    messages that are encode to actually do its job. The only 2
    required fields in the encoded format are the url and the params
    fields that are required to launch the task somehow.
    """
    def __init__(self, decode=json.loads, encode=json.dumps,
                 defaulturl="http://localhost:8000/",
                 reactor=reactor, getPage=client.getPage):

        self.reactor = reactor
        self.decode = decode
        self.encode = encode
        self.getPage = getPage
        defaultscheme, defaultnetloc, _, _, _, _ = urlparse.urlparse(defaulturl)

        self.defaultscheme = defaultscheme
        if not defaultscheme:
            self.defaultscheme = "http"

        self.defaultnetloc = defaultnetloc
        if not defaultnetloc:
            self.defaultnetloc = "localhost"

        self.prehooks = []
        self.posthooks = []

    def addPrehook(self, fun):
        """
        Add a pre-processing function. Pre-hooks are run before the
        request for the task is made, they take one argument that is
        the task at hand. They should be careful to return a deferred
        when they execute code that is asynchronous otherwise the task
        might be finished when the request is still running (which
        might not be an issue but might be unexpected).

        Pre-hooks are inserted after the ones already existing so that
        a "system" hook has precedence over everything else.

        All pre-hooks must execute correctly otherwise the task is
        requeued.

        Pre-hooks can decide to filter a task out by setting the
        'filter' field in them. However this won't stop the excepthook
        or the post-hooks from running for cleanup reasons, if you
        don't want them to run check for the 'filter' property and
        skip execution from inside the hook.

        @param fun: A function that takes one argument "task".
        @type fun: C{function}
        """
        self.prehooks.append(fun)

    def addPosthook(self, fun):
        """
        Add a post-processing function. Post-hooks are run after the
        request for the task is made, they take 2 arguments: the just
        executed task and the result of the task execution returned
        from the request. As for the pre-hooks be sure to return
        deferreds when you want the other post-hooks to wait for you.

        Post-hooks are inserted before the ones already existing so that
        a "system" hook is run as the last one to wrap up state.

        All post-hooks must execute correctly otherwise even if the
        task has already completed it's considered a failure and is
        requeued.

        @param fun: A function that takes two arguments: "task" and "result"
        @type fun: C{function}
        """
        self.posthooks.insert(0, fun)

    def _executeHooks(self, hooks, *args, **kwargs):
        """
        Execute the passed hooks in order and by isolating them.
        """
        first = hooks[0]
        d = defer.maybeDeferred(first, *args, **kwargs)
        for hook in hooks[1:]:
            d.addCallback(lambda _, f=hook: f(*args, **kwargs))
        # You are here for multiple reasons:
        # Hooks can't pass arguments to processTask
        # and because in this way they always return
        # None when everything is fine, and a string
        # will be returned in case of errors.
        d.addCallback(lambda _: None)
        return d

    def taskReceived(self, task):
        """
        Receives an decoded message from some source, checks for its
        validity through TTL, and starts the chain of execution for
        the given task.

        @param task: decoded task to be executed
        @type task: C{dict}
        """
        if not task:
            log.msg("Error with task %s, discarding..." % (task,))
            return

        ttl = task.get("ttl", 0)
        if ttl:
            if qc.parse_date(task['timestamp']) + timedelta(seconds=ttl) < qc.now():
                # This message is too old, discard it
                log.msg("Discarding %s because its ttl of %ss expired" % (task, ttl))
                return

        d = defer.succeed(None)

        if self.prehooks:
            d.addCallback(lambda _: self._executeHooks(self.prehooks, task))

        d.addCallback(lambda _: self.processTask(task))

        if self.posthooks:
            d.addCallback(lambda result: self._executeHooks(self.posthooks, task, result))
        return d

    def normalizeUrl(self, url):
        """
        Normalizes a URL in order to create a complete one from a
        possible partial in the task metadata.

        @param url: a url to a given executor service.
        @type url: C{str}
        """
        scheme, netloc, path, params, query, fragment = urlparse.urlparse(url)
        if not scheme:
            scheme = self.defaultscheme
        if not netloc:
            netloc = self.defaultnetloc
        return urlparse.urlunparse((scheme, netloc, path, params, query, fragment))

    def makeRequest(self, url, task):
        """
        Send a request to a given url with the given data and
        timeout. It expects the return format to be the same used to
        decode the messages.

        @param url: a full URL to a web server
        @type url: C{str}

        @param timeout: Maximum wait time for a task.
        @type timeout: C{int}

        @param data: An encoded data string.
        @type data: C{str}
        """
        timeout = task.get('timeout', 0)
        data = self.encode(task)
        return self.getPage(url, method="POST", postdata=data, timeout=timeout,
                            headers={"Content-Length": str(len(data))}
                  ).addCallback(self.decode)

    def processTask(self, task):
        """
        Actually execute a given task

        @param task: The task to execute
        @type task: not really specified, should be dict-like.
        """
        # we do something nasty but cool here.
        # task is a dictionary because that's the protocol.
        # dictionaries are mutable. if one of the pre-hooks adds
        # a filter = True field to the dictionary then the task is
        # not started and is instead filtered.
        if task.get('filter', False):
            log.msg("Task %s was filtered by pre-hooks" % (task,))
            return

        timeout = task.get('timeout', 0)
        url = task['url'].encode('utf-8')

        fullurl = self.normalizeUrl(url)
        return self.makeRequest(fullurl, task)
