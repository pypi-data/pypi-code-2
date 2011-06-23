import pdb
from bdb import Breakpoint
from interfaces import IDebugger
from zope.interface import implements
import sys
import inspect

class Debugger(object):
    """ Pdb wrapper, so we can jump in and out. """
    implements(IDebugger)
    
    def __init__(self):
        self._debugger = pdb.Pdb()
    
    def is_installed(self):
        return False
    
    def get_breaks(self):
        return Breakpoint.bpbynumber
    
    def set_temporary(self,bid,value):
        b = Breakpoint.bpbynumber[bid]
        b.temporary = value
    
    def add_break(self,filename,line,temporary=1):
        self._debugger.set_break(filename,line,temporary=temporary)
        if len(self.get_breaks()) == 1:
            self.enable()

    def remove_break(self,id):
        self._debugger.clear_bpbynumber(id)
            
    def reset(self):
        """ Clear all breaks and disable """
        self._debugger.clear_all_breaks()
        self._debugger.reset()
        self.disable()
    
    def enable(self):
        self._debugger.reset()
        
        # I have no idea why this works, but this appears to be required to 
        # force the debugger to not drop to an interactive prompt immediately
        # upon leaving the current frame.
        fr = inspect.stack()[0][0]
        self._debugger.botframe = fr
        
        sys.settrace(self._debugger.trace_dispatch)
    
    def disable(self):
        # Should probably check we're actually the trace function
        sys.settrace(None)