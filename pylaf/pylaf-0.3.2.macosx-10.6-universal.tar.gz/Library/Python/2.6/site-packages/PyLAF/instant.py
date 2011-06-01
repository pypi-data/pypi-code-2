# coding: utf-8
'''
インスタントPyLAFの試験実装
'''
import Tkinter, inspect, os, imp
from framework import iscontain, popcnf, App, Component, Port
from plot import BasePlot

def findroot(widget):
    try:
        widget.master.master
    except AttributeError:
        return widget
    return findroot(widget.master)

def findtoplevel(widget):
    cls  = widget.master.__class__
    if not (cls == Tkinter.Toplevel or cls == Tkinter.Tk):
        return findtoplevel(widget.master)
    return widget.master

class AvailableApps(dict):
    def __init__(self,root):
        dict.__init__(self)
        self.check(root)
    def check(self,widget):
        for name in widget.children: self.check(widget.children[name])
        if iscontain(widget,App):
            t, c = widget.master.title(), widget.component
            self['%s:%s' % (t,c.__class__.__name__)] = c

class AvailableComponent(dict):
    def __init__(self,cwd):
        dict.__init__(self)
        #
        pylaf = imp.load_module('PyLAF',*imp.find_module('PyLAF'))
        mods  = {}
        for key,module in inspect.getmembers(pylaf,lambda x:inspect.ismodule(x)): mods[key] = module
        plt   = inspect.getmembers(mods['plot'],lambda x:inspect.isclass(x) and inspect.getmro(x).__contains__(BasePlot))
        for key,cls in plt: self[key] = cls
        #
        for fname in os.listdir(cwd):
            if fname.endswith('.py'):
                mname = fname.replace('.py','')
                try:
                    m = imp.load_module(mname,*imp.find_module(mname,[cwd]))
                    cs = inspect.getmembers(m,lambda x:inspect.isclass(x) and inspect.getmro(x).__contains__(Component))
                    for key,cls in cs: self[key] = cls
                except SyntaxError: pass
                except ImportError: pass
                except AttributeError: pass
        for key in ['BasePlot','EasyComponent','Component']:
            try: del self[key]
            except KeyError: pass

class PortListbox(Tkinter.Listbox):
    def __init__(self,master,**key):
        frame = Tkinter.Frame(master)
        self.apps    = apps    = popcnf('apps',key)
        self.appvar  = appvar  = Tkinter.StringVar()
        appvar.set(apps.keys()[0])
        self.appvar_trace = appvar.trace('w',self.set)
        self.portvar = Tkinter.StringVar()
        Tkinter.OptionMenu(frame,appvar,*apps.keys()).pack()
        self.makeScrolledListbox(Tkinter.Frame(frame),**key); self.master.pack()
        self.bind('<ButtonRelease-1>',self.buffer)
        Tkinter.Entry(frame,textvariable=self.portvar).pack()
        self.set()
        for m in (Tkinter.Pack.__dict__.keys() + Tkinter.Grid.__dict__.keys() + Tkinter.Place.__dict__.keys()):
            m[0] == '_' or m == 'config' or m == 'configure' or setattr(self, m, getattr(frame, m))
    def makeScrolledListbox(self,master,**key):
        yscroll = Tkinter.Scrollbar(master,orient=Tkinter.VERTICAL)
        yscroll.pack(side=Tkinter.RIGHT,fill=Tkinter.BOTH)
        Tkinter.Listbox.__init__(self,master,yscrollcommand=yscroll.set,selectmode=Tkinter.SINGLE,**key)
        self.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        yscroll.config(command=self.yview)
    def buffer(self,*args):
        selection = Tkinter.Listbox.get(self,0,Tkinter.END)[int(self.curselection()[0])]
        self.portvar.set(selection)
    def set(self,*args):
        self.pdic = pdic = PortCollector(self.apps[self.appvar.get()])
        self.delete(0,Tkinter.END)
        self.insert(Tkinter.END,*[key for key in pdic])
    def get(self): return self.pdic[self.portvar.get()]
    def clear(self): self.portvar.set('')
    def destroy(self):
        self.appvar.trace_vdelete('w',self.appvar_trace)
        Tkinter.Listbox.destroy(self)

class PortCollector(dict):
    def __init__(self,component):
        dict.__init__(self)
        self.collect(component)
    def collect(self,component,prefix='.'):
        m = inspect.getmembers(component,lambda x:iscontain(x,Port))
        for key,obj in m: self[prefix+key] = obj
        m = inspect.getmembers(component,lambda x:iscontain(x,Component))
        for key,obj in m:
            if not key == 'master': self.collect(obj,prefix+'%s.' % key)

class ClassListbox(Tkinter.Listbox):
    '''立ち上げ可能コンポーネントクラスの一覧、App(Equipment)でローンチ
    '''
    def __init__(self,master,**key):
        frame = Tkinter.Frame(master)
        self.title = Tkinter.Entry(frame); self.title.pack()
        self.cmps = AvailableComponent(os.getcwd())
        self.makeScrolledListbox(Tkinter.Frame(frame),**key); self.master.pack()
        Tkinter.Button(frame,text='Launch',command=self.launch).pack()
        self.insert(Tkinter.END,*[key for key in self.cmps])
        self.bind('<Double-1>',self.launch)
        for m in (Tkinter.Pack.__dict__.keys() + Tkinter.Grid.__dict__.keys() + Tkinter.Place.__dict__.keys()):
            m[0] == '_' or m == 'config' or m == 'configure' or setattr(self, m, getattr(frame, m))
    def makeScrolledListbox(self,master,**key):
        yscroll = Tkinter.Scrollbar(master,orient=Tkinter.VERTICAL)
        yscroll.pack(side=Tkinter.RIGHT,fill=Tkinter.BOTH)
        Tkinter.Listbox.__init__(self,master,yscrollcommand=yscroll.set,selectmode=Tkinter.SINGLE,**key)
        self.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
        yscroll.config(command=self.yview)
    def launch(self,*args):
        try:
            selection = self.get(0,Tkinter.END)[int(self.curselection()[0])]
        except IndexError: return
        o = App(Tkinter.Toplevel(findroot(self)),self.cmps[selection])
        title = self.title.get()
        if title == '': title = self.cmps[selection].__name__
        o.master.title(title)
        o.pack()
        findtoplevel(self).destroy()
        
class Linker(Tkinter.Toplevel):
    '''起動したクラスのポートメンバの一覧、ローンチされているイクイップメントの一覧（コンボメニュー）、
    イクイップメントを選択するとそのポートメンバの一覧を表示
    ポートを選択してリンクボタンを押す
    '''
    def __init__(self, master=None, cnf={}, **kw):
        root = findroot(master)
        Tkinter.Toplevel.__init__(self,findtoplevel(master),cnf,**kw)
        apps = AvailableApps(root)
        self.src = src = PortListbox(self,apps=apps); src.pack(side=Tkinter.LEFT)
        title = apps.keys()[0]
        for key,obj in apps.items():
            if master == obj: title = key
        src.appvar.set(title)
        Tkinter.Button(self,text='oo',command=self.link).pack(side=Tkinter.LEFT)
        self.tgt = tgt = PortListbox(self,apps=apps); tgt.pack(side=Tkinter.LEFT)
    def link(self):
        try:
            src = self.src.get()
            tgt = self.tgt.get()
            src.link(tgt)
            tgt.set(src.get())
        except KeyError: pass
        self.src.clear()
        self.tgt.clear()
    def destroy(self):
        self.src, self.tgt = None, None
        Tkinter.Toplevel.destroy(self)
        