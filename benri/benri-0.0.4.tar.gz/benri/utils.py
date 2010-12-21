# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import selector, os

from paste.httpexceptions import HTTPException

def daemonize():
    """
    Spawn a daemon process of the current executable. It is recommended to use this
    when running a server-process.
    """
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    # adapted from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
    try:
        pid = os.fork()
    except OSError, e:
        print >>sys.stderr, "Daemon could not be started: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    if pid == 0:
        os.setsid()
            
        try:
            pid = os.fork()
        except OSError, e:
            print >>sys.stderr, "Daemon could not be started: %d (%s)" % (e.errno, e.strerror)
            sys.exit(1)

        if pid == 0:               
            os.chdir("/")   #don't prevent unmounting....
            os.umask(0)
        else:
            os._exit(0) # see comments in the recipe
    else:
        os._exit(0)

    import resource
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if (maxfd == resource.RLIM_INFINITY):
        maxfd = 1024
      
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:
            pass
            
    os.open(os.devnull, os.O_RDWR)	# standard input (0)

    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1)			# standard output (1)
    os.dup2(0, 2)			# standard error (2)

def test_wrapper(wsgiapp):
    """Returns a selector-wsgiapp wrapping the given wsgiapp instance. Useful
       for testing when using paste fixtures.
    """

    s = selector.Selector()
    s.slurp(wsgiapp.routes)
    
    return ErrorMiddleware(s)
