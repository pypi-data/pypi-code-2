"""
This is a helper module for the framework start-up process.  It takes care of:

  * Initialising logging.
  * Instantiating the application's main loop subclass.
  * Starting the basic framework services.
"""

import logging
import sys

# Initialize logging
from . import loginit

# This should be downgraded to warning or info level at the application's discretion.
logging.root.setLevel(logging.DEBUG)

# Instantiate app
app = None

def InitializeApp(appClass, appname, redirectOutput=True, redirectLoggerToStdOut=False, **kw):
    loginit.Init(redirectOutput=redirectOutput, redirectLoggerToStdOut=redirectLoggerToStdOut)

    logging.root.info("Application %s starting up", appname)

    # The user has provided a subclass of 'sake.loop.App' which will get
    # instantiated here.
    global app
    app = appClass(appname, **kw)
    app.InitConfigFiles()
    # At this point the application is expected to have read its configuration
    # files and we can notify it to establish state based on the values
    # contained within them.
    app.PostInitConfigFiles()

    # Install base services
    from . import session
    from . import process
    from . import login

    # The basic set of services which run as part of sake supporting logic.
    # SessionManager must be started first, then TaskletPool.  Both of them must be started
    # synchronously, since only after TaskletPool is started are tasklet (Process.New) available.
    services = [
        session.SessionManager,
        process.TaskletPool,
        login.LoginService,
    ]
    # Give the application a chance to specify its own custom services that
    # should be started.
    services.extend(app.GetAppServiceClasses())

    app.InitServices(services)

    return app
