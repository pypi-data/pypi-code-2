"""
process module - implements process concepts. yessirre.
"""

from collections import deque
import logging
import sys
import traceback
import stackless
import stacklesslib.main
import stacklesslib.locks

from .const import WAIT_INFINITE, WAIT_CHECK
from .errors import TimeoutError
from . import util


class Tasklet(stackless.tasklet):
    """Tasklet wrapper.
    Adds top-level exception handler and keeps reference to its owner
    """

    def __new__(cls, process, func):

        def Handler(*args, **kw):
            self.RunFunc(process, func, args, kw)

        self = super(Tasklet, cls).__new__(cls, Handler)
        self.SetupState(process)
        return self

    def SetupState(self, process):
        """
        Set up the tasklet with initial attributes pertaining to the process, returning
        any such previous attributes (oldstate)
        """
        try:
            oldstate = self.name, self.locals, self.process, self.session
        except AttributeError:
            oldstate = None

        self.name = "tasklet:%s:%s" % (process.name, process.taskletCounter)
        self.locals = None
        self.process = None # Set in Process.OnTaskletEnter()
        self.session = util.GetSession() # Inherit parent session
        process.taskletCounter += 1
        return oldstate

    def RestoreState(self, oldstate):
        """
        Restore the tasklet attributes to those that were before SetupState()
        """
        if oldstate:
            self.name, self.locals, self.process, self.session = oldstate

    def RunFunc(self, process, func, args, kwargs):
        """
        Run a function, along with the proper top level error handling and
        process bookkeeping.
        SetupState() must have been called previously.
        """
        process.OnTaskletEnter(self)
        try:
            self.retval = func(*args, **kwargs)
        except Exception, e:
            process.log.exception("Unhandled top-level exception in process '%s'", process.name)
            self.exception = e
        finally:
            process.OnTaskletLeave(self)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<Tasklet object at %s: %r alive=%s, scheduled=%s, blocked=%s>" % (hex(id(self)), self.name, self.alive, self.scheduled, self.blocked)

    def Trace(self):
        sys.stdout.write(repr(self) +"\n")
        traceback.print_stack(self.frame, file = sys.stdout)


class Process(object):
    """Process monitor"""

    processCounter = 1000
    taskletCounter = 1
    processStartAsync = True #by default, a process is started using a worker tasklet

    def __init__(self):
        self.running = True
        self.name = None # CreateProcess in loop module sets this at a later time.
        t = stackless.getcurrent()

        # when running in BSD environment, the initialize thread is not main
        # we use t.process to check if the thread is created by mini-framework.
        if t.is_main or not hasattr(t,"process"):
            self.session = None
        else:
            self.session = t.process.session
        self.tasklets = set()
        self.createCount = 0
        self.destroyCount = 0
        self.pid = Process.processCounter
        Process.processCounter += 1
        self.waitqueue = None

    def __repr__(self):
        return "<Process %r with %s running tasklets>" % (self.name, len(self.tasklets))

    def StartProcess(self):
        """StartProcess() ->  None
        Called by app when process or service starts
        """
        pass

    def StopProcess(self):
        """StopProcess() ->  None
        Called when process or service stops
        """
        pass

    def New(self, fn, *args, **kw):
        #Create tasklets using the TaskeletPool service.
        t =  self.app.GetService("TaskletPool").Tasklet(self, fn)
        return t(*args, **kw)

    def Wait(self, timeout = WAIT_INFINITE):
        """Wait(timeout) -> bool
        Wait on all tasklets in the process.
        If the function returns 'True', all tasklets have exited.
        If the function returns 'False, one or more tasklets are still busy.
        'timeout' is timeout in milliseconds. Use WAIT_INFINITE for no timeout.
        If 'timeout' is WAIT_CHECK, the function returns immediately.

        If the calling tasklet is part of the process, the function will return when
        all other tasklets have exited (i.e. it will not deadlock itself or raise an error).
        """
        if self.tasklets:
            # Make sure we're not waiting on ourself and not the last runnable tasklet.
            t = stackless.getcurrent()
            if (t in self.tasklets and len(self.tasklets) == 1) or stackless.getruncount() < 2:
                return True

            if timeout == WAIT_CHECK:
                return len(self.tasklets) == 0
            else:
                if self.waitqueue is None:
                    self.waitqueue = stacklesslib.locks.Event()
                # Speak "stacklesslib" for no timeout.
                if timeout == WAIT_INFINITE:
                    timeout = None
                try:
                    self.waitqueue.wait(timeout)
                except stacklesslib.util.WaitTimeoutError:
                    msg = "%s tasklets still alive in %s after %.1f seconds of waiting."
                    raise TimeoutError(msg % (len(self.tasklets), self.name, timeout))
        return True

    def OnTaskletEnter(self, tasklet):
        tasklet.process = self
        self.tasklets.add(tasklet)
        self.createCount += 1
        ## too noisy self.log.debug("TaskletEnter: %s", tasklet)

    def OnTaskletLeave(self, tasklet):
        ## too noisy self.log.debug("TaskletExit: %s", tasklet)
        tasklet.process = None
        self.tasklets.remove(tasklet)
        self.destroyCount += 1

        if not self.tasklets and self.waitqueue:
            self.waitqueue.set()
            self.waitqueue = None

        self.app.dbg.TaskletExiting(tasklet)

    def Kill(self, reason = None):
        if reason:
            reason = "Process killed: " + reason
        else:
            reason = "Process killed."

        self.log.info("Killing process '%s' and its %s tasklets, reason: %s", self.name, len(self.tasklets), reason)
        self.running = False
        self.StopProcess()

        self.app.OnProcessDestroyed(self)

        # Kill all associated tasklets
        killSelf = False
        current = stackless.getcurrent()

        for t in self.tasklets.copy():
            t.killReason = reason
            if current == t:
                killSelf = True
            else:
                t.kill()

                del t # Need to unbind so it won't show up in orphaned tasklet report on system exit.

        # Wait until all tasklets are dead
        self.Wait()

        if killSelf:
            current.kill()


class TaskletPool(Process):
    """
    A class that recycles tasklets.  This is useful not as a performance improvement, but to limit the number
    of actual tasklet IDs in use, when implementing C level code that uses the tasklet ID as an index to
    some sort of TLS structure.
    """

    serviceName = "TaskletPool"
    serviceIncludes = []
    processStartAsync = False

    def __init__(self):
        Process.__init__(self)
        self.queue = deque()
        self.maxlen = 20  #How many idle tasklets to keep

    def StopProcess(self):
        self.Flush()

    def Flush(self):
        """
        Clear the queue of idle tasklets
        """
        while self.queue:
            self.DropTasklet()

    def Tasklet(self, process, func):
        """
        Emulate the constructor of the Tasklet object.  Tries to get the most recently used idle
        tasklet.  If none are available, a new is created.
        Returns a callable that can be used to bind arguments to the call.
        """
        while len(self.queue):
            channel = self.queue.pop()
            if (channel.balance):
                tasklet = channel.queue
                #self.log.debug("Reusing tasklet %r", tasklet)
                oldstate = tasklet.SetupState(process)
                def Callable(*args, **kwargs):
                    channel.send( (process, func, args, kwargs, oldstate) )
                    return tasklet
                return Callable

        #queue is empty, start a new tasklet
        tasklet = self.app.CreateRawTasklet(self, self.TaskletFunc)
        #self.log.debug("Creating tasklet %r", tasklet)
        oldstate = tasklet.SetupState(process)
        def Callable2(*args, **kwargs):
            # By passing the function and arguments in directly, we are
            # binding them into the call stack and they will never get
            # garbage collected.  So we pass them in, in a list, which
            # can subsequently be cleared limiting their lifetime.
            return tasklet([ process, func, args, kwargs, oldstate ])

        return Callable2

    def DropTasklet(self):
        """
        Remove the oldest Tasklet from the queue, telling it to stop.
        """
        channel = self.queue.popleft()
        if channel.balance:
            channel.send(None)
        #self.log.debug("Dropping tasklet %r", tasklet)

    def TaskletFunc(self, mutableArgs):
        """
        The main worker function for each tasklet managed by the TaskletPool
        Takes as arguments the initial process, function and arguments to execute.
        """

        #start by executing the initial function
        process, func, args, kwargs, oldstate = mutableArgs
        # Prevent the arguments from living forever in the call stack.
        del mutableArgs[:]

        t = stackless.getcurrent()
        t.RunFunc(process, func, args, kwargs)
        t.RestoreState(oldstate)

        #then, get new work from the queue
        while True:
            # We will block on GetWork, waiting for more, so ensure we
            # do not keep the objects for the last piece of work alive
            # until that point.
            work = process = func = args = kwargs = oldstate = None
            work = self.GetWork()
            if not work:
                return #well, that's it, then.
            #perform the assigned work
            process, func, args, kwargs, oldstate = work
            t.RunFunc(process, func, args, kwargs)
            t.RestoreState(oldstate)

    def GetWork(self):
        """
        Get the next piece of work to perform on the behalf of a user, or None
        """
        if self.maxlen > 0:
            channel = stackless.channel()
            channel.preference = 1 #for make-runnable behaviour
            self.queue.append(channel)
            while len(self.queue) > self.maxlen:
                self.DropTasklet()
            return channel.receive()
