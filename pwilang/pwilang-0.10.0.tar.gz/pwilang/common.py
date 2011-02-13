
import sys
from os.path import relpath, abspath

error_flag = False
__problems = []

class color:
    '''
        Namespace used for terminal formating.
    '''
    gray = '\033[1;30m'
    red = '\033[1;31m'
    green = '\033[1;32m'
    yellow = '\033[1;33m'
    blue = '\033[1;34m'
    magenta = '\033[1;3m'
    cyan = '\033[1;36m'
    white = '\033[1;37m'
    crimson = '\033[1;38m'

    hred = '\033[1;41m'
    hgreen = '\033[1;42m'
    hbrown = '\033[1;43m'
    hblue = '\033[1;44m'
    hmagenta = '\033[1;45m'
    hcyan = '\033[1;46m'
    hgray = '\033[1;47m'
    hcrimson = '\033[1;48m'

    normal = '\033[1;m'

class Problem (object):
    ''' A problem, with all of its associated information. '''

    def __init__ (self, text, line, error=False):
        global error_flag
        self.text = text
        self.line = line
        if error:
            error_flag = True
        self.error = error

    def display (self, out=sys.stderr):
        if self.line:
            out.write ('%s%s%s:%s%d%s: ' %
                (color.blue, relpath (self.line.fname), color.normal, 
                 color.green, self.line.linenb, color.normal))
        else:
            out.write ('%s<unk>%s:%s%d%s: ' %
                (color.blue, color.normal, color.green, self.line.linenb, color.normal))
        if self.error:
            out.write ('%serror%s: ' % (color.red, color.normal))
        else:
            out.write ('%swarning%s: ' % (color.yellow, color.normal))
        out.write ('%s\n' % self.text)
        
def warning (text, line=None):
    ''' Adds a warning to the problem list. '''

    __problems.append (Problem (text, line))

def error (text, line=None):
    ''' Adds an error to the problem list. '''

    __problems.append (Problem (text, line, True))

def flush_errors (out=sys.stderr):
    ''' Displays all the errors on the screen and clear the error flag. '''

    for problem in __problems:
        problem.display (out)

    global error_flag
    error_flag = False


__deps = None
def deps_start ():
    ''' Starts the dependancy tracker. '''

    global __deps
    __deps = []

def deps_add (path):
    ''' Add a dependancy to the dependancy list '''

    if __deps is not None:
        __deps.append (abspath (path))

def deps_flush ():
    ''' Empty the list of dependancy and return its contents. '''

    global __deps
    tmp = __deps
    __deps = None
    return tmp

