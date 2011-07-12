try:
    import gdb
except ImportError:
    pass
else:
    import pygdb2.gdb_commands # side effects

import os
import pdb
import traceback
import ctypes
import signal
import signal2

def execute(*cmds):
    """
    Execute all the commands inside gdb.
    """
    cmds = '\n'.join(cmds)
    buf = ctypes.create_string_buffer(cmds)
    value = signal2.sigval_t()
    value.sigval_ptr = ctypes.cast(buf, ctypes.c_void_p)
    signal2.sigqueue(os.getpid(), signal.SIGUSR2, value) # caught by GDB

def set_trace():
    """
    Pop up a gdb prompt
    """
    execute()

def enter_pdb(sig, frame):
    """
    Signal handler which opens a pdb prompt
    """
    print 'Signal received, entering pdb'
    print 'Traceback:'
    traceback.print_stack(frame)
    pdb.Pdb().set_trace(frame)
    
signal.signal(signal.SIGUSR1, enter_pdb)
