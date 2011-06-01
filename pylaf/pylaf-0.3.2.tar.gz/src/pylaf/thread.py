# coding: utf-8

import Tkinter
from core import Component, Port, Output

class StateCanceled(Exception): pass

class Buffer(Component):
    def __init__(self,master=None,name=None):
        Component.__init__(self,master,name)
        self.receive = Port(None).bind(self._set)
        self.send    = Output(None).bind(self.flush)
        self._last   = None
    def _set(self):
        self._last = self.receive.get()
    def flush(self):
        if not self._last == None:
            self.send.set_now(self._last)
            self._last = None
            
class Polling(Tkinter.Frame):
    def __init__(self,master=None,interval=200,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.interval = interval
        self.value    = Port(None)
        self._id      = None
        self._polling()
    def start(self):
        self._polling()
    def stop(self):
        if not self._id == None:
            self.after_cancel(self._id)
    def _polling(self):
        self.value.set_now(None)
        self._id = self.after(self.interval,self._polling)
        
