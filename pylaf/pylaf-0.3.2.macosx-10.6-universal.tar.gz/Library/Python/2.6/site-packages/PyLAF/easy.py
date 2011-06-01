# coding: utf-8

from numpy import array
from framework import Component, Port, Frame, iscontain
from framework import DoubleVar, IntVar, StringVar, BooleanVar
from widgets import GridPane, Menu
from inspect import getmembers, stack, getargvalues
from instant import Linker, ClassListbox, findtoplevel
import Tkinter

class EasyPortContainer:
    def __init__(self):
        self.colcount = 0

class EasyComponent(Component,EasyPortContainer):
    PLOTTER = None
    def __init__(self,master):
        Component.__init__(self,master)
        EasyPortContainer.__init__(self)
        self._menu    = None
        if not self.PLOTTER == None:
            self.sig_out  = Port(array([]))
            self.plotter  = Component(self)
            dummy = self.PLOTTER()
            for key,info in getmembers(dummy,lambda x:iscontain(x,Port)):
                setattr(self.plotter,key,Port(info.get()))
            dummy.destroy()
    def gui(self,master,pltcnf={},cnf={},**kw):
        frm = Frame(master)
        if not self.PLOTTER == None: self.mkplotter(frm,pltcnf).pack()
        o = EasyGrid(frm,self); o.pack()
        setattr(master,'console',o)
        return frm
    def mkplotter(self,master,pltcnf={}):
        v = self.__class__.PLOTTER(master,pltcnf); v.ax.plot(); v.canvas.show()
        setattr(master.master,'plotter',v)
        for key,info in getmembers(v,lambda x:iscontain(x,Port)):
            getattr(self.plotter,key).insertlink(0,info)
        self.sig_out.insertlink(0,v.sig_in);
        return v
    def menu(self,master,cnf={},**kw):
        link   = lambda:Linker(self)
        launch = lambda:ClassListbox(Tkinter.Toplevel(findtoplevel(self))).pack()
        menu = [['PyLAF', ['Launch...',launch],['Link to...',link]]]
        try:
            for item in self._menu: menu.append(item)
        except TypeError: pass
        return EasyMenu(master,list=menu,cnf=cnf,**kw)
    def destroy(self):
        self._menu = None
        Component.destroy(self)

class EasyPort(Port):
    def _inckey(self,caller,key=None):
        if key == None:
            caller.colcount += 1
            self.sortkey = caller.colcount
        else:
            self.sortkey = key
    def _caller(self):
        '''
        下記ブログに掲載されていたコードを使わせてもらった
        http://d.hatena.ne.jp/Kazumi007/20090914/1252915940
        '''
        try:
            framerecords = stack()
            framerecord  = framerecords[2]
            frame        = framerecord[0]
            arginfo      = getargvalues(frame)
            return arginfo.locals['self'] if 'self' in arginfo.locals else None
        finally:
            del frame
        return None
    def grid(self,master): pass
    

class EntryPort(EasyPort):
    def __init__(self,variable,label='',key=None,**opt):
        EasyPort.__init__(self,variable)
        self._inckey(self._caller(),key=key)
        self.label = label
        self.opt = opt
    def grid(self,master):
        subject = self.subject.get()
        if type(subject) == float:
            tkvar = DoubleVar(self,**self.opt)
        elif type(subject) == int:
            tkvar = IntVar(self,**self.opt)
        elif type(subject) == bool:
            tkvar = BooleanVar(self,**self.opt)
        else:
            tkvar = StringVar(self,**self.opt)
        master.entry(self.label,tkvar)
        
class TrigPort(EasyPort):
    def __init__(self,variable,label='',key=None):
        EasyPort.__init__(self,variable)
        self._inckey(self._caller(),key=key)
        self.label = label
    def grid(self,master):
        master.trig(self.label,BooleanVar(self))

class TriggeredCheckbuttonPort(EasyPort):
    def __init__(self,variable,label='',key=None):
        EasyPort.__init__(self,variable)
        self._inckey(self._caller(),key=key)
        self.label = label
    def grid(self,master):
        master.triggered_checkbutton(self.label,BooleanVar(self))

class EasyGrid(GridPane):
    def __init__(self,master,component,cnf={},**kw):
        GridPane.__init__(self,master,cnf,**kw)
        ms = getmembers(component,lambda x:iscontain(x,EasyPort))
        ms.sort(lambda x,y:cmp(x[1].sortkey,y[1].sortkey))
        for m,o in ms: o.grid(self)

class EasyMenu(Menu):
    def __init__(self,master=None,list=None,cnf={},**kw):
        Menu.__init__(self,master,cnf,**kw)
        for m in list: self.add_children(self,m)
    def add_children(self,parent,children):
        if type(children[1]) == list:
            cascade = Tkinter.Menu(parent)
            parent.add_cascade(label=children[0],menu=cascade)
            for m in children[1:]: self.add_children(cascade,m)
        else:
            label,func = children
            parent.add_command(label=label,command=func)

