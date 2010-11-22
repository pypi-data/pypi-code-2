import sys, os, string, subprocess, time
from os.path import dirname, join
from unweb.recipe import ploneftp
cmd_map = dict(
    fg=('-n',),
    start = (),
)

def main(args):
    pidfile = '%s/ploneftp.pid' % args[0]
    os.environ['PLONEFTP_ROOT'] = args[0]
    if len(args) < 2:
        print "Usage: ploneftp start|stop|fg"
        return
    if args[1] == 'stop':
        try:
            pid = int(file(pidfile).read())
            os.unlink(pidfile)
            os.kill(pid, 15)
            print "PloneFTP stopped"
        except:
            print "PloneFTP not running"
        return
    elif args[1] == 'start':
        try:
            pid = int(file(pidfile).read())
            print "PloneFTP already running"
            return
        except:
            pass
        py_file = join(dirname(ploneftp.__file__), 'zope_ftpd.py')
        logfile = '%s/ploneftp.log'  % args[0]
        try:
            pid = os.fork()
        except OSError, e:
            print "ploneftp did not start"
    
        # parent (calling) process is all done
        if pid != 0:
            print "ploneftp started"
            f = open(pidfile,'w')
            f.write(str(pid))
            f.close()
            return

        # detach from controlling terminal (to make child a session-leader)
        logf = open(logfile,'a')
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
        os.dup2(logf.fileno(),sys.stdout.fileno())
        os.dup2(logf.fileno(),sys.stderr.fileno())
        print "testing log"
        os.setsid()
        ploneftp.zope_ftpd.main(args[0])
	log.close()
    elif args[1] == 'fg':
        ploneftp.zope_ftpd.main(args[0])
