"""
loginit module - Initializes appropriate log functions in logging module
"""

import logging
import logging.handlers
import os
import sys

from .const import PLATFORM_PS3
from . import logutil


def Init(redirectOutput=True, redirectLoggerToStdOut=False):
    if redirectLoggerToStdOut:
        # define a Handler which writes INFO messages or higher to the sys.stdout

        # Blue patches stdout to some crappy object that doesn't properly implement
        # all the file methods that are required and expected.. i.e. stream.flush()
        # We add a proxy here that stubs in this method.
        localStdOut = sys.stdout
        if not hasattr(localStdOut, "flush"):
            class LameStdOutFixer:
                def __init__(self, stream):
                    self.stream = stream
                def __getattr__(self, key):
                    return getattr(self.stream, key)
                def flush(self):
                    pass
            localStdOut = LameStdOutFixer(localStdOut)

        console = logging.StreamHandler(localStdOut)
        console.setLevel(logging.INFO)

        # set a format which is simpler for console use
        formatter = logging.Formatter('>> %(message)s')

        # tell the handler to use this format
        console.setFormatter(formatter)

        # add the handler to the root logger
        logging.root.addHandler(console)

    # If there is no place to redirect logs to (logserver, ue3), then fall back to outputting them to a file.
    if len(logging.root.handlers) == 0:
        if sys.platform == PLATFORM_PS3:
            root = "/app_home"
        else:
            root = ""

        # Add rotating file handler - rotate daily and keep last 30 days of logs
        logdir = os.path.join(root, "logs")
        if not os.path.isdir(logdir):
            os.mkdir(logdir)

        filename = os.path.join(root, "logs", "ding.log")
        file = logging.handlers.TimedRotatingFileHandler(filename, when = "d", backupCount = 30, encoding = "utf-8")
        file.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s'))
        logging.root.addHandler(file)

        sys.stdout.write("Falling back on logging to file: %s\n" % filename)

    if redirectOutput:
        sys.stdout.write("Redirecting stdout and stderr to the logger.\n")
        sys.stdout = logutil.LogStream(logging.INFO)
        sys.stderr = logutil.LogStream(logging.ERROR)

def RestoreStdOutput():
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
