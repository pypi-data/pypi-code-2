"""
Code reloading integration.

This implements the ability to detect changes to source code and automatically
reload files when this happens.  The actual reloading logic is implemented in
the :py:mod:`sake.xreload` module.

.. note::

   At this time this module only supports the Windows platform.
"""

import inspect
import logging
import os
import py_compile
import stat
import sys
import time
import types

from .platform.win32 import win32api
from . import util
from .xreload import xreload


class SpyFolder:
    """Spy on folder changes using Win32 notification mechanism and do automatic
    recompile and reload.
    """

    def __init__(self, waitables, path):

        self.handle = None
        self.runningCheckAt = 0
        self.startedAt = time.time()
        self.processed = {} # Key is filename, value is last compile time

        self.path = os.path.abspath(path)

        if not os.path.exists(self.path):
            raise RuntimeError("SpyFolder: Can't spy on non-existing folder %s" % self.path)

        self.handle = win32api.FindFirstChangeNotification(self.path, True, win32api.FILE_NOTIFY_CHANGE_LAST_WRITE)
        waitables.InsertHandle(self.handle, self)
        logging.root.info("AutoCompiler: Now spying on %s", self.path)

    def __del__(self):
        if self.handle:
            win32api.FindCloseChangeNotification(self.handle)

    def OnObjectSignaled(self, handle, abandoned):
        # Called by win32api.Waitables utility
        if abandoned:
            return

        assert(handle == self.handle)
        win32api.FindNextChangeNotification(self.handle)

        now = util.GetTime()
        if now - self.runningCheckAt < 2.0: # Ignore file changes for at least 2 secs.
            return

        self.runningCheckAt = now

        self.ProcessFolder()

    def PollForChanges(self):
        """If any file has been modified in the folder or subfolders, a recompile is triggered."""

        if self.handle and win32api.WaitForSingleObject(self.handle):
            # Continue to spy, find the file(s) and reload the module
            win32api.FindNextChangeNotification(self.handle)
            self.ProcessFolder()

    def ReloadFile(self, filename):
        """Reloads a file module given a file name."""

        # Make absolute path from filename and strip the extension, as it can be .py, .pyc or .pyo.
        filename = os.path.abspath(filename).rsplit(".", 1)[0]
        for mname, module in sys.modules.items():
            if not module or not hasattr(module, "__file__") or hasattr(module, "__loader__"):
                continue

            # By comparing the abspath from sys.modules with the 'filename' argument, we can
            # match it to a loaded module and call reload() on it.
            try:
                modulefile = os.path.abspath(inspect.getfile(module)).rsplit(".", 1)[0]
            except TypeError:
                # Most likely not a module.
                continue
            if modulefile == filename:
                logging.root.info("AutoCompiler: Reloading %s", module)
                module = xreload(module)

    def ProcessFolder(self):
        """Search the folder and subfolders for out of date .py files and compile
        them. If the module is loaded, the running code is fixed accordingly
        """

        toProcess = []
        c = 0
        for root, dirs, files in os.walk(self.path):
            for name in files:
                c += 1
                if not name.lower().endswith(".py"):
                    continue

                sourceFile = os.path.join(root, name)
                sourceFileDate = os.stat(sourceFile)[stat.ST_MTIME]
                lastCompile = self.processed.get(sourceFile, self.startedAt)

                if sourceFileDate > lastCompile:
                    toProcess.append(sourceFile)
                    self.processed[sourceFile] = sourceFileDate


        if toProcess:
            # Give file a chance to write itself to disk
            win32api.Sleep(250)
            for sourceFile in toProcess:
                self.ReloadFile(sourceFile)
