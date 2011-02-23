# -*- test-case-name: anymeta.test.test_queue -*-
#
# Copyright (c) 2009-2011 Mediamatic Lab
# See LICENSE for details.

"""
Module containing a submit queue. The L{PersistentQueue} class is a
generic class for the submission of items to an online service.

The queue can be saved on program exit and retrieved on startup.
Items in the queue are processed L{PersistentQueue.processItems} through a
user-defined callback function which is expected to return a deferred
result. On the failure of this deferred, the corresponding item gets
placed back in the queue for later retry. On the deferred's success,
the item gets removed from the queue.

There is no order preservation: On an item's failure, it is pushed
back to the end of the queue and thus is retried on a later moment.
"""

import os

import simplejson

from twisted.internet import defer
from twisted.python import log
from twisted.internet import error
from twisted.web import error as http_error

class PersistentQueue(object):
    """
    Implementation of a queue for the failsafe processing of items
    through an API call.

    Note that L{PersistentQueue.save} needs explicitly be called for
    the queue to be saved.
    """

    # Private variables
    _queue = None
    _state_file = None

    def __init__(self, state_file = None):
        self._queue = []

        if state_file:
            self._state_file = state_file
        self._state_file = os.path.expanduser(self._state_file)
        if os.path.exists(self._state_file):
            self._queue = simplejson.load(open(self._state_file, 'r'))


    def save(self):
        """
        Saves the current queue to the state file. When the queue is
        empty, it is not saved and the state file is thrown away.
        """
        if len(self._queue):
            log.msg("Saving submit queue state.")
            simplejson.dump( self._queue, open(self._state_file, 'w'))

        elif os.path.exists(self._state_file):
            os.unlink(self._state_file)



    def add(self, item):
        """
        Adds an item to the queue.
        """
        self._queue.append(item)


    def size(self):
        """
        Returns the current size of the queue.
        """
        return len(self._queue)


    def processBatch(self, callable, max=10):
        """
        Process the next batch of items which are waiting to be
        sent. For every item, the callable is called which is expected
        to return a deferred.

        This function itself returns a deferred which will fire when
        the entire current batch has completed. Return value of this
        deferred is a (success count, fail count) tuple.
        """

        if not self._queue:
            log.msg("Nothing in the queue...")
            return defer.succeed(True)

        items, self._queue = self._queue[:max], self._queue[max:]
        log.msg("Submitting %d item(s)" % len(items))

        ds = []
        for item in items:
            ds.append(callable(item))

        l = defer.DeferredList(ds, consumeErrors = True)

        def cb(result):
            i = 0
            success_count = 0
            fail_count    = 0

            for state, r in result:
                if not state or not r:
                    # submission of item failed, re-add it to queue
                    self._queue.append(items[i])
                    log.err("Submit of %s failed!" % items[i])
                    log.err(r)
                    fail_count += 1
                else:
                    # submission succeeded
                    success_count += 1
                i += 1
            return success_count, fail_count

        l.addCallback(cb)
        return l


class Task(object):
    value = None
    status = 'new'

    def __init__(self, value):
        self.value = value


class TaskNotAssociatedError(Exception):
    """
    This task is not associated with this queue.
    """


class TaskQueue(object):
    """
    An event driven task queue.

    Values may be added as usual to this queue. When an attempt is
    made to retrieve a value when the queue is empty, a Deferred is
    returned which will fire when a value becomes available.
    """

    def __init__(self):
        self.waiting = []
        self._tasks = set()
        self.pending = []

    def createTask(self, value):
        return self.createTasks([value])[0]


    def createTasks(self, values):
        tasks = []
        for value in values:
            task = Task(value)
            task.queue = self
            self._tasks.add(task)
            tasks.append(task)
        return tasks


    def _enqueue(self, task):
        """
        Enqueue a task.

        If a consumer is waiting, its callback is called with the task,
        otherwise it is in the queue of pending tasks.
        """
        if self.waiting:
            task.status = 'in_progress'
            self.waiting.pop(0).callback(task)
        else:
            self.pending.append(task)


    def put(self, value):
        """
        Create a new task and add it the queue.

        When retrieving the enqueued task, the value is stored in the
        C{value} attribute of the task instance.

        @param value: The value that represents the task.
        @return: The new task.
        """
        return self.putMany([value])[0]


    def putMany(self, values):
        """
        Create tasks and add it the queue.

        When retrieving the enqueued task, the value is stored in the
        C{value} attribute of the task instance.

        @param value: The value that represents the task.
        @return: The new task.
        """
        tasks = self.createTasks(values)
        for task in tasks:
            self._enqueue(task)
        return tasks


    def _cancelGet(self, d):
        """
        Remove a deferred d from our waiting list, as the deferred has been
        canceled.

        @param d: The deferred that has been cancelled.
        """
        self.waiting.remove(d)


    def get(self):
        """
        Attempt to retrieve and remove a task from the queue.

        The returned task will contain the value as it was queued with L{put}
        in the C{value} attribute. As the queue keeps track of created tasks,
        it is required to call L{retry}, L{fail} or L{done} after
        processing the task.

        @return: A Deferred which fires with the next task available in the
            queue.
        """
        if self.pending:
            task = self.pending.pop(0)
            task.status = 'in_progress'
            return defer.succeed(task)
        else:
            d = defer.Deferred(self._cancelGet)
            self.waiting.append(d)
            return d


    def retry(self, task):
        """
        Retry a task.

        The task, gotten through L{get}, is requeued for later retry.
        """
        if not task in self._tasks:
            raise TaskNotAssociatedError()

        task.status = 'retryable'
        self._enqueue(task)


    def fail(self, task):
        """
        Fail a task.

        The task, gotten through L{get}, is not requeued for later retry,
        but kept in L{tasks} for later inspection. The task can be retried
        by calling L{retry}.
        """

        if not task in self._tasks:
            raise TaskNotAssociatedError()

        task.status = 'failed'


    def succeed(self, task):
        """
        Succeed a task.

        The task, gotten through L{get}, is not requeued and removed from
        its record of tasks in L{tasks}.
        """

        if not task in self._tasks:
            raise TaskNotAssociatedError()

        task.status = 'done'
        self._tasks.remove(task)



class SQLiteTaskQueue(object):
    """
    An event driven task queue.

    Values may be added as usual to this queue. When an attempt is
    made to retrieve a value when the queue is empty, a Deferred is
    returned which will fire when a value becomes available.
    """

    def __init__(self, connection):
        self._connection = connection
        self._cursor = connection.cursor()

        self.waiting = []
        self.pending = []

        self.fillQueue()


    def fillQueue(self):
        try:
            self._cursor.execute("""SELECT rowid, value, status FROM tasks
                                    WHERE status != 'failed'""")
        except self._connection.OperationalError:
            # table does not exist. Try to create it
            self._cursor.execute("""CREATE TABLE tasks (value text,
                                                        status text)""")
            self._connection.commit()
        else:
            for rowid, value, status in self._cursor:
                try:
                    task = Task(simplejson.loads(value))
                except ValueError:
                    log.msg("Invalid task in storage: %d, %r" % (rowid, value))
                    continue

                task.identifier = rowid
                task.status = status
                task.queue = self
                self._enqueue(task)


    def createTask(self, value):
        return self.createTasks([value])[0]


    def createTasks(self, values):
        tasks = []
        for value in values:
            task = Task(value)
            self._cursor.execute("""INSERT INTO tasks (value, status)
                                    VALUES (?, 'new')""",
                                 (simplejson.dumps(value),))
            task.identifier = self._cursor.lastrowid
            task.queue = self
            tasks.append(task)
        self._connection.commit()
        return tasks


    def _enqueue(self, task):
        """
        Enqueue a task.

        If a consumer is waiting, its callback is called with the task,
        otherwise it is in the queue of pending tasks.
        """
        if self.waiting:
            task.status = 'in_progress'
            self.waiting.pop(0).callback(task)
        else:
            self.pending.append(task)


    def put(self, value):
        """
        Create a new task and add it the queue.

        When retrieving the enqueued task, the value is stored in the
        C{value} attribute of the task instance.

        @param value: The value that represents the task.
        @return: The new task.
        """
        task = self.createTask(value)
        self._enqueue(task)
        return task


    def putMany(self, values):
        """
        Create tasks and add it the queue.

        When retrieving the enqueued task, the value is stored in the
        C{value} attribute of the task instance.

        @param value: The value that represents the task.
        @return: The new task.
        """
        tasks = self.createTasks(values)
        for task in tasks:
            self._enqueue(task)
        return tasks


    def _cancelGet(self, d):
        """
        Remove a deferred d from our waiting list, as the deferred has been
        canceled.

        @param d: The deferred that has been cancelled.
        """
        self.waiting.remove(d)


    def get(self):
        """
        Attempt to retrieve and remove a task from the queue.

        The returned task will contain the value as it was queued with L{put}
        in the C{value} attribute. As the queue keeps track of created tasks,
        it is required to call L{retry}, L{fail} or L{done} after
        processing the task.

        @return: A Deferred which fires with the next task available in the
            queue.
        """
        if self.pending:
            task = self.pending.pop(0)
            task.status = 'in_progress'
            return defer.succeed(task)
        else:
            d = defer.Deferred(self._cancelGet)
            self.waiting.append(d)
            return d


    def retry(self, task):
        """
        Retry a task.

        The task, gotten through L{get}, is requeued for later retry.
        """
        if task.queue != self:
            raise TaskNotAssociatedError()

        self._cursor.execute("""UPDATE tasks SET status='retryable'
                                WHERE rowid=?""",
                             (task.identifier,))
        if self._cursor.rowcount < 1:
            raise TaskNotAssociatedError()

        self._connection.commit()

        task.status = 'retryable'
        self._enqueue(task)


    def fail(self, task):
        """
        Fail a task.

        The task, gotten through L{get}, is not requeued for later retry,
        but kept in L{tasks} for later inspection. The task can be retried
        by calling L{retry}.
        """

        if task.queue != self:
            raise TaskNotAssociatedError()

        self._cursor.execute("UPDATE tasks SET status='failed' WHERE rowid=?",
                             (task.identifier,))
        if self._cursor.rowcount < 1:
            raise TaskNotAssociatedError()

        self._connection.commit()

        task.status = 'failed'


    def succeed(self, task):
        """
        Succeed a task.

        The task, gotten through L{get}, is not requeued and removed from
        its record of tasks in L{tasks}.
        """

        if task.queue != self:
            raise TaskNotAssociatedError()

        self._cursor.execute("""DELETE FROM tasks WHERE rowid=?""",
                             (task.identifier,))
        if self._cursor.rowcount < 1:
            raise TaskNotAssociatedError()

        self._connection.commit()

        task.status = 'done'



class RetryError(Exception):
    """
    Container of a failure to signal that retries are possible.
    """
    def __init__(self, failure):
        Exception.__init__(self, failure)
        self.subFailure = failure



class TimeoutError(Exception):
    """
    Raised when the queue runner reaches a set timeout without a value.
    """



class TaskQueueRunner(object):
    """
    Basic submission queue runner.

    This runner makes no assumptions on the types of tasks and retry
    behaviour. Once L{run} is called, it reschedules itself according
    to L{delay}.

    @ivar timeout: Timeout in seconds for cancelling the get on
        the queue on each run of L{run}. The cancelling causes C{deferred} to
        be fired with a L{TimeoutError}.
    @type timeout: C{int}
    @ivar deferred: Deferred that errbacks with L{TimeoutError} when no
        value was put before the timeout set with C{timeout} expires.
    @type deferred: L{defer.Deferred}
    """

    clock = None
    delay = 0
    timeout = 0
    deferred = None

    def __init__(self, queue, callable, start=True):
        self.queue = queue
        self.callable = callable

        if self.clock is None:
            from twisted.internet import reactor
            self.clock = reactor

        self.deferred = defer.Deferred()
        if start:
            self.run()


    def run(self):
        """
        Execute one task and reschedule.

        If C{timeout} is set on this runner, and the timeout expires, no
        rescheduling is done afterwards and this runner is considered done.

        @return: This runner's deferred that fires with a L{TimeoutError} when
            the timeout expires.
        """
        def succeed(_, task):
            self.queue.succeed(task)

        def retry(failure, task):
            failure.trap(RetryError)
            log.err(failure.value.subFailure, "Retrying task")
            self.queue.retry(task)

        def fail(failure, task):
            log.err(failure, "Failing task")
            self.queue.fail(task)


        def call(task):
            d = self.callable(task.value)
            d.addCallback(succeed, task)
            d.addErrback(retry, task)
            d.addErrback(fail, task)
            return d

        def trapTimeout(failure):
            failure.trap(defer.CancelledError)
            self.deferred.errback(TimeoutError())

        d = self.queue.get()
        d.addCallback(call)
        d.addCallback(lambda _: self.clock.callLater(self.delay, self.run))
        d.addErrback(trapTimeout)
        d.addErrback(self.deferred.errback)

        if self.timeout:
            self.clock.callLater(self.timeout, d.cancel)

        return self.deferred


CONNECT_BACKOFF = {
        'delay': 0.25,
        'maxDelay': 16,
        'factor': 2,
        }

HTTP_BACKOFF = {
        'delay': 10,
        'maxDelay': 240,
        'factor': 2,
        }

class APIQueuer(object):
    """
    Helper for queueing tasks that do HTTP based API calls.

    Given a queue and a controller instance, this helper can be used to
    add new tasks as method calls on the controller. It will retry tasks
    that fail with network connection errors and HTTP 5xx errors with
    reasonable back-off algorithms. Calls that raise other exceptions will
    result in failed tasks. The controller methods may return deferreds.

    Network connection errors will start off with a 0.25s delay, that
    doubles on every retry with a maximum of 16s. HTTP errors start with a
    10s delay, doubling to a maximum of 240s.

    @ivar start: Start the runner immediately.
    @type start: C{bool}
    """

    retryableErrors = {
            error.ConnectError: 'connect',
            error.TimeoutError: 'connect',
            error.ConnectionClosed: 'connect',
            http_error.Error: 'http',
            }


    def __init__(self, queue, controller, start=True):
        self.queue = queue
        self.controller = controller
        self.runner = TaskQueueRunner(self.queue, self.doMethod, start)
        self.errorState = None


    def add(self, method, args):
        """
        Add a new task.

        This creates a new task with a named method on L{controller} and
        a dict of arguments to be passed to that method.

        @param method: Method name on controller.
        @type method: C{str}.
        @param args: Arguments to the method.
        @type args: C{dict}.
        """
        value = (method, args)
        self.queue.put(value)


    def trap_connect(self, failure):
        """
        Trap connect errors.
        """
        return CONNECT_BACKOFF


    def trap_http(self, failure):
        """
        Trap HTTP 5xx errors.
        """
        exc = failure.value

        if 500 <= int(exc.status) < 600:
            return HTTP_BACKOFF
        else:
            return False


    def trapErrors(self, failure):
        """
        Trap errors to check retryability and apply back-off algoritms.
        """
        excType = failure.trap(*self.retryableErrors.keys())

        errorState = self.retryableErrors[excType]

        try:
            method = getattr(self, 'trap_' + errorState)
        except AttributeError:
            return failure

        backoff = method(failure)

        if not backoff:
            return failure

        if self.errorState != errorState:
            self.errorState = errorState
            self.runner.delay = backoff['delay']
        else:
            self.runner.delay = min(backoff['maxDelay'],
                                    self.runner.delay * backoff['factor'])

        raise RetryError(failure)


    def doMethod(self, value):
        """
        Execute one task.

        This takes a task, and executes the method embedded in it on the
        controller. When the method fails, the exception is checked to
        determine retryability and applies back-off algorithms accordingly.
        """

        def succeeded(result):
            self.errorState = None
            self.runner.delay = 0

        def trapNotRetryable(failure):
            if not failure.check(RetryError):
                self.errorState = None
                self.runner.delay = 0

            return failure

        method, args = value
        d = defer.maybeDeferred(getattr(self.controller, method), args)
        d.addCallback(succeeded)
        d.addErrback(self.trapErrors)
        d.addErrback(trapNotRetryable)
        return d
