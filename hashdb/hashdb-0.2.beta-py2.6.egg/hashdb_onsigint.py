import signal
import sys

def isatty(f):
    try:
        return f.isatty()
    except:
        return False

def _onsignal(signum, frame):
    if isatty(sys.stdout):
        sys.stdout.flush()
        print '\x1B[0K\x1B[?25h\033[0m' # Clear line, Show cursor, Reset style
    sys.stdout.flush()
    exit(-1)
signal.signal(signal.SIGINT, _onsignal)
