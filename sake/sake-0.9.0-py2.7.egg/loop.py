# Application loop

import atexit
from errors import CoreError, ServiceNotFoundError
import heapq
import logging
import os
import sys
import stackless
import stacklesslib.main
from stacklesslib.util import ValueEvent

# HACK: matti - can't depend on asyncore and select if we are backend server
try:
    import asyncore
    import select

    #This should be better abstracted from asyncore, but hey!
    if hasattr(select, "poll"):
        asyncore_poll = asyncore.poll2
    else:
        asyncore_poll = asyncore.poll
    useAsyncore = True
except ImportError:
    useAsyncore = False

from . import config
from .const import ROLE_SERVICE, APP_ROLE_UNKNOWN, PLATFORM_WIN32
from .dbghelp import DbgHelp
from .process import Process, Tasklet
from . import platform
if sys.platform == "win32":
    from .platform.win32 import win32api

from . import util


sakeConfigDefaults = [
        ("Settings",    "fakeLatencySeconds",   0.0),
        ("Logging",     "networkPackets",       False),
        ("Logging",     "networkRPC",           False),
]




FPS_WARNING_THRESHOLD = 250.0 # Log out a warning if fps goes above this number.
PUMP_WARNING_THRESHOLD = 1.0

USER_CONFIG_FILENAME = "sake.ini"

DEFAULT_BUILD_NUMBER = 999999999


class App(stacklesslib.main.MainLoop):
    """
    The application base class.  An application will need to subclass this and
    customise it to their needs.    
    """

    role = APP_ROLE_UNKNOWN
    useCodeReloading = True
    pumpWindowsMessages = False
    timeout = 0

    dataPath = None
    appName = "Untitled Application"

    def __init__(self, appName, **kw):
        super(App, self).__init__()
    
        self.appName = appName

        # Set up log channels
        self.log = logging.getLogger("CORE.App")
        self.logp = logging.getLogger("CORE.Process")

        # Detect branch and game root path and set platform specific values
        if sys.platform == PLATFORM_WIN32:
            # Initialize win32 waitable objects utility and autocompile feature
            self.waitables = win32api.Waitables()

        # Local members
        self.services = util.Bunch() # For dot notation
        self.processes = []
        self.process = self.CreateProcess("App main process")
        self.running = True

        # Timing, scheduling and performance
        self.clock = util.GetTime() # Set each time Pump is called - used in scheduling
        self.cycleCount = 0 # Number of times Pump has been called
        self.fps = 0 # Number of loops per second (i.e. frames per sec)
        self.lastFpsCheck = util.GetTime()
        self.lastFpsCycleCount = 0
        self.laptime = 0.0 # Last Pump call in seconds
        self.lastPumpTime = None

        # Service startup serialization
        self.serviceQueue = {} # Key is service name

        # Debugging aid.
        self.dbg =  DbgHelp()

        self.clientSession = None

        # Application-specific data structures.
        self.appConfigDefaults = []

        # An experiment
        atexit.register(self._Shutdown)

    def HasRole(self, roleMask):
        """ Check if the application role includes the set bits in :literal:`roleMask`. """
        return (self.role & roleMask) == roleMask

    def SetCodeReloadingPath(self, codePath):
        self.log.info("Engaging code reloading for path: %s", codePath)
        import autocompile
        self.spy = autocompile.SpyFolder(self.waitables, codePath)

    def SetDataPath(self, dataPath):
        """
        Tell the application that its data can be found in the path specified
        by :literal:`dataPath`.
        """
        self.dataPath = dataPath

    def SetWin32WindowName(self, windowName):
        """
        Set a pretty console Window title to identify this app instance.
        
        .. note::

            Windows only.
        """
        win32api.SetConsoleTitle(util.GetAppTitle(windowName))

    def GetAppServiceClasses(self):
        """
        References to classes which should be started.
        """
        return []

    def InitConfigFiles(self):
        self.config = ReadSakeConfigFile(self.dataPath, self.appConfigDefaults)
        # We blindly write out the file to ensure the version on disk has all
        # the default values present.  But we really only need to do the write
        # only if it has changed.  Not worth it.
        config.WriteConfigFile(self.dataPath, USER_CONFIG_FILENAME, self.config)

    def PostInitConfigFiles(self):
        """ Override to trigger logic when the config file is loaded.  """
        pass

    def SetAppConfigDefaults(self, defaults):
        self.appConfigDefaults = defaults

    def GetVersionString(self):
        return "unversioned"

    def AbsPath(self, path):
        """
        Joins branch root (i.e. //depot/core/MAIN) and 'path' and returns an absolute path.
        For packaged apps, the branch root is considered the folder above the bin folder.
        """
        return os.path.abspath(path)

    def CreateRawTasklet(self, taskletPool, taskletPoolFunc):
        """
        Creates a raw tasklet object for the tasklet pool to use.
        Allows custom applications to specialise the type of tasklet that is created.
        """
        return Tasklet(taskletPool, taskletPoolFunc)

    def CreateProcess(self, name, processClass = Process, isService = False):
        """CreateProcess(name) -> Process
        """

        process = processClass()
        test = process.pid # If this reference fails, a child of Process didn't call its parents init method
        process.app = self
        process.name = name
        process.log = self.logp

        if isService:
            process.log = logging.getLogger("CORE.Process.%s" % process.serviceName)

            def StartProcess():
                try:
                    self._StartProcess(process)
                except Exception:
                    self._FlushServiceQueue(process, "Service '%s' failed during StartProcess()." % name)
                    return # Let this tasklet just wither away silently

                setattr(self.services, process.name, process)
                self._FlushServiceQueue(process, None)
                self.processes.append(process)

            # Resolve service dependencies
            for svcname in getattr(processClass, "serviceIncludes", []):
                setattr(process, svcname, self.GetService(svcname))

            # Assign a new session
            if name == "sessionManager":
                sessMgr = process # Chicken'n'egg avoidance logic
            else:
                sessMgr = self.GetService("sessionManager")

            process.session = sessMgr.CreateSession(userid = "auto", username = "svc.%s" % name, role = ROLE_SERVICE)
            StartProcess()
        else:
            self.processes.append(process)


        return process


    def OnProcessDestroyed(self, process):
        # Remove gracefully from process and service list
        self.processes.remove(process)

        if process.name in self.services:
            del self.services[process.name]

    def _StartProcess(self, process):
        process.StartProcess()
        self.log.info("Service started: %s", process.name)

    def _FlushServiceQueue(self, service, error):
        serviceEvent = self.serviceQueue[service.serviceName]

        if error:
            self.log.exception(error)
            serviceEvent.abort(CoreError, "Dependant service '%s' failed to start" % service.serviceName)
        else:
            serviceEvent.set(service)

        if service.serviceName in self.serviceQueue: # Must check - it might have been deleted on a different tasklet.
            del self.serviceQueue[service.serviceName]

        if not self.serviceQueue:
            self.log.info("Service startup finished in %.1f seconds.", util.GetTime() - util.clockStart)

    def InitServices(self, serviceList):
        """InitServices(serviceList) -> None
        Initialize services. 'serviceList' is a list of Process classes.
        """
        for service in serviceList:
            if not issubclass(service, Process):
                raise RuntimeError("App Init: Service class '%s' must inherit from Process." % service)
            if hasattr(self.services, service.serviceName):
                raise RuntimeError("App Init: Service with name '%s' already exists." % service.serviceName)

            def CreateProcess_(service):
                try:
                    self.CreateProcess(service.serviceName, service, True)
                except Exception:
                    self._FlushServiceQueue(service, "Initialization of service '%s' failed." % service.serviceName)

            self.serviceQueue[service.serviceName] = ValueEvent()

            if service.processStartAsync:
                self.process.New(CreateProcess_, service)
            else:
                CreateProcess_(service)


    def GetService(self, serviceName):
        """GetService(serviceName) -> service
        Returns a named service. This call may block until the service is available
        """
        if serviceName in self.services:
            return self.services[serviceName]
        elif serviceName in self.serviceQueue:
            return self.serviceQueue[serviceName].wait()
        else:
            raise ServiceNotFoundError("GetService: Service '%s' not found." % serviceName)

    def OnObjectSignaled(self, handle, abandoned):
        """The default signal. Not used at the moment"""
        pass

    def BeNice(self, slice = 50):
        """BeNice(slice) -> None
        Calls Yield() if current tasklet has been running for more than 'slice' milliseconds.
        """

        # TODO: Implement this properly, and preferably as monkeypatched nylon version.
        self.sleep(0)

    def Yield(self):
        """Yield() -> None
        Suspends the current tasklet and schedules it immediately.
        """
        self.sleep(0)

    def Sleep(self, seconds):
        """Suspend the current tasklet for 'seconds' seconds."""
        self.sleep(seconds)

    def _Shutdown(self, reason = "Python engine shutting down"):
        """_Shutdown(reason) -> None

        Kills all processes and suspends pumping. Do not call directly - use Quit() instead.
        """
        if not self.running:
            return

        self.running = False
        self.log.info("Shutdown: %s", reason)

        for process in self.processes[::-1]:
            try:
                process.Kill(reason)
            except TaskletExit:
                pass

        self.dbg.ReportShutdown()
        self.log.info("Application loop has shut down.")

    def Run(self):
        """Run() -> None
        Runs application until no more."""

        while self.running:
            try:
                self.Pump()
            except Exception, e:
                self.log.exception("Exception in main loop")
                raise

    def _WaitForNextEvent(self, timeoutOverride=None):
        """Wait until any OS handle is signaled, a Win32 message is available, the
        next sleeper is due for a wake-up, or not at all if a yielder needs
        resuming.
        The function returns how many seconds it spent Wait-ing (see Pump below).
        """
        if timeoutOverride is None:
            if stacklesslib.main.event_queue.queue_a:
                wakeAt = stacklesslib.main.event_queue.queue_a[0][0]
                diff = wakeAt - self.clock
                if diff < 0:
                    waitFor = 0
                else:
                    waitFor = int(diff * 1000)
            else:
                waitFor = self.timeout

            if waitFor > self.timeout:
                waitFor = self.timeout
        else:
            waitFor = timeoutOverride

        try:
            start = util.GetTime()
            ret = self.waitables.Wait(waitFor)
        except Exception:
            self.log.exception("Wait failed")

        return util.GetTime() - start

    def _UpdateLoopCounters(self):
        now = util.GetTime()
        self.clock = now
        self.cycleCount += 1

        # Calculate fps
        elapsed = now - self.lastFpsCheck
        if elapsed > 1.0:
            cycles = self.cycleCount - self.lastFpsCycleCount
            self.fps = cycles / elapsed
            self.lastFpsCycleCount = self.cycleCount
            self.lastFpsCheck = now

            if self.fps > FPS_WARNING_THRESHOLD:
                self.log.warning("FPS suspiciously high: %.1f. (current lap time: %.3f ms.)", self.fps, self.laptime * 1000.0)

    def _ResumeSleepers(self):
        # Resume sleepers and abort time-outs
        self.wakeup_tasklets(self.clock)

    def _AdjustSleepers(self, delta):
        """
        We want to alter all the wake-up times of timeouts or sleepers by a
        set amount.  The consistent change in value should also keep the
        heapq structure consistent.
        """
        timed_event_queue = stacklesslib.main.event_queue.queue_a
        self.log.debug("Adjusting the wake-up time of %d entries", len(timed_event_queue))
        for i, entry in enumerate(timed_event_queue):
            timed_event_queue[i] = (entry[0] + delta, entry[1])

    def Pump(self):
        """Pumps tasklets and stuff.
        """
        start = util.GetTime() # Do simple benchmark check for this function

        if self.lastPumpTime is not None and start - self.lastPumpTime > PUMP_WARNING_THRESHOLD:
            delta = start - self.lastPumpTime
            self.log.warning("Python has not been ticked for %0.2f seconds.  Making adjustments to workaround problems this may cause.", delta)

            # Not being pumped for long periods of time, perhaps because of blocking
            # map loading that may take over four minutes, means that tasklets waiting
            # for replies may now time out, despite the reply packet sitting on the
            # socket waiting to be read.
            self._AdjustSleepers(delta)

        self._ResumeSleepers()
        if useAsyncore:
            self._PumpAsyncore()

        # Run without pre-emptive scheduling
        self._RunScheduler()

        # TODO: If a tasklet was pre-emptively scheduled, report it, then kill it.

        self._UpdateLoopCounters()
        if sys.platform == PLATFORM_WIN32:
            waitTime = self._WaitForNextEvent()
        else:
            waitTime = 0
 
        # Dispatch windows messages
        if self.pumpWindowsMessages:
            if not win32api.PumpWindowsMessages():
                self.Quit("WM_QUIT posted.")

        ##self.dbg.ReportGarbage()
        self.laptime = util.GetTime() - start - waitTime
        self.lastPumpTime = start

    def _RunScheduler(self):
        self.run_tasklets(20000000)

    def handle_run_error(self, ei):
        """ Override default 'stacklesslib' error handling. """
        self.log.error("stackless.run caught an error", exc_info=ei)

    def _PumpAsyncore(self):
        try:
            asyncore_poll(0.0)
        except Exception, e:
            self.log.exception("asyncore.poll failed")
            raise

    def Quit(self, reason):
        """Quit(reason) -> None

        Raises SystemExit with the 'reason' string.
        """
        self.log.info("Quitting: %s", reason)
        raise SystemExit(reason)

    # Client notionality.

    def GetClientSession(self):
        return self.clientSession

    def SetClientSession(self, session):
        self.clientSession = session


def ReadSakeConfigFile(dataPath, appConfigDefaults=()):
    defaultEntries = sakeConfigDefaults[:]
    defaultEntries.extend(appConfigDefaults)
    return config.ReadConfigFile(dataPath, USER_CONFIG_FILENAME, defaultEntries)
