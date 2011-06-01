# coding: utf-8

#import weakref, inspect, platform, types, time
import re, functools, threading, Queue, weakref
import utils.gui, core#, utils.functions
#from functools import partial
from utils.gui.tkwidgets import *
from scipy import log10

def classname(obj): return repr(obj.__class__).split('.')[-1].split(' ')[0]

class Projection:
    class Through:
        @classmethod
        def forward(cls,x):  return x
        @classmethod
        def backward(cls,x): return x
    class INV:
        @classmethod
        def forward(cls,x):  return 1./x
        @classmethod
        def backward(cls,x): return 1./x
    class DB:
        @classmethod
        def forward(cls,x):  return 10.*log10(x)
        @classmethod
        def backward(cls,x): return 10.**(x/10.)

class Bind:
    class Callback:
        def __init__(self):
            self.callbacks = []
        def __call__(self,*args,**kwargs):
            for callback in self.callbacks:
                callback(*args,**kwargs)
        def bind(self,callback):
            self.callbacks.append(callback)
    def bind(self,event,callback):
        try: self.bind_callbacks
        except AttributeError:
            self.bind_callbacks = {}
        if not self.bind_callbacks.has_key(event):
            cb = Bind.Callback()
            self.bind_callbacks[event] = cb
            Tkinter.Widget.bind(self,event,cb)
        self.bind_callbacks[event].bind(callback)
        
class Entry(Bind,Tkinter.Entry):
    def __init__(self,master=None,value='',format='%s',range=None,projection=Projection.Through,cnf={},**kw):
        Tkinter.Entry.__init__(self,master,cnf,**kw)
        self.projection = projection
        self.format = format
        self.old = None
        self.range = range
        self.value = core.Port(None).bind(self._forward)
        self.value.set(value)
        self.bind('<Escape>',self._forward) # ESCキーが押されたら値を破棄する
        self.bind('<Return>',self._backward) # RETURNキーが押されたら値を確定する
        self.bind('<FocusOut>',self._forward) # FOCUSが失われたら値を確定する
    def _forward(self,*args):
        self.delete(0,len(self.get()))
        self.insert(0,self.format % self.projection.forward(self.value.get()))
    def _backward(self,*args):
        old = self.projection.forward(self.value.get())
        try: # 文字列を変換できればその値を
            new = type(self.value.get())(self.get())
        except ValueError: # できなければ零を代入する
            new = type(self.value.get())('0')
        if self.range:
            if not self.range(new): new = old # もし範囲に入っていなければ以前の値に戻す
        self.value.set(self.projection.backward(new)) # Portで保持しているオブジェクト型に変換してセット
            
class EntryTable(Tkinter.Frame):
    def __init__(self,master=None,row=1,column=1,format='%s',rowlabel=None,columnlabel=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.value = core.Port([['' for c in range(column)] for r in range(row)]).bind(self._forward)
        self.joint = []
        self.row   = row
        self.column = column
        # カラムラベルの生成
        if columnlabel:
            if type(columnlabel) == str:
                for j in range(column): Label(self,text=re.sub('%d','%d' % (j+1),columnlabel)).grid(row=0,column=j+1)
            else:
                for j,label in enumerate(columnlabel): Label(self,text=label).grid(row=0,column=j+1)
        # ローラベルの生成
        if rowlabel:
            if type(rowlabel) == str:
                for i in range(row): Label(self,text=re.sub('%d','%d' % (i+1),rowlabel)).grid(row=i+1,column=0)
            else:
                for i,label in enumerate(rowlabel): Label(self,text=label).grid(row=i+1,column=0)
        # エントリーウィジェットの生成
        for i in range(row):
            joint = []
            for j in range(column):
                #print i,j
                joint.append(core.Port('').bind(functools.partial(self._backward,i=i,j=j)))
                #w = Entry(self,name='item%d%d' % (i,j),format=format)
                w = Entry(self,format=format)
                w.grid(row=i+1,column=j+1,sticky=Tkinter.W+Tkinter.E)
                joint[-1].link(w.value)
            self.joint.append(joint)
    def _forward(self):
        self._forward_called = True
        value = self.value.get()
        for i in range(self.row):
            for j in range(self.column):
                if i >= len(value) or j >= len(value[0]):
                    self.joint[i][j].set(0)
                else:
                    self.joint[i][j].set(value[i][j])
        del self._forward_called
    def _backward(self,i,j):
        try: self._forward_called
        except AttributeError:
            value = self.value.get()
            if i < len(value) and j < len(value[0]):
                value[i][j] = self.joint[i][j].get()
                self.value.set(value)
    def entryconfig(self,**kw):
        for key in self.children:
            entry = self.children[key]
            if not entry.__class__ == Entry: continue
            entry.config(**kw)
            
class MultipleEntries(Tkinter.Frame):
    def __init__(self,master=None,name=None,column=2,projection=None,frameoption={},cnf={},**kw):
        Tkinter.Frame.__init__(self,master,name=name,cnf=frameoption)
        self.value      = core.Port(['' for i in range(column)]).bind(self._forward)
        self.mode       = core.Port(None).bind(self._forward)
        self.joint      = []
        self.column     = column
        self.projection = projection
        for i in range(column):
            self.joint.append(core.Port('').bind(self._backward))
            w = Entry(self,name='item%d' % i,cnf=cnf,**kw)
            w.grid(row=0,column=i)
            self.joint[-1].link(w.value)
    def _forward(self):
        value = self.value.get()[:self.column]
        if self.projection:
            forward = self.projection[self.mode.get()][0]
            value = forward(value)
        for o,v in zip(self.joint,value): o.set(v)
    def _backward(self):
        value    = [o.get() for o in self.joint]
        if self.projection:
            backward = self.projection[self.mode.get()][1]
            value    = backward(value)
        self.value.set(value)
        
class Label(Tkinter.Label):
    def __init__(self,master=None,format='%s',cnf={},**kw):
        Tkinter.Label.__init__(self,master,cnf,**kw)
        self.format = format
        self.value  = core.Port('').bind(self.updated)
    def updated(self):
        self.configure(text=self.format % self.value.get())

class LabelTable(Tkinter.Frame):
    def __init__(self,master=None,name=None,row=1,column=1,rowlabel=None,columnlabel=None,width=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,name=name)
        self.value = core.Port([['' for c in range(column)] for r in range(row)]).bind(self._forward)
        self.joint = []
        self.row   = row
        self.column = column
        # カラムラベルの生成
        if columnlabel:
            if type(columnlabel) == str:
                for j in range(column): Label(self,text=re.sub('%d','%d' % (j+1),columnlabel)).grid(row=0,column=j+1)
            else:
                for j,label in enumerate(columnlabel): Label(self,text=label).grid(row=0,column=j+1)
        if rowlabel:
            if type(rowlabel) == str:
                rowlabel = [re.sub('%d','%d' % (i+1),rowlabel) for i in range(row)]
            for i,label in enumerate(rowlabel):
                w = Label(self,text=label)
                w.grid(row=i+1,column=0)
                w.configure(anchor=Tkinter.W)
                if width: w.configure(width=width[0])
        for i in range(row):
            joint = []
            for j in range(column):
                joint.append(core.Port(''))#.bind(self._backward))
                w = Label(self,name='item%d%d' % (i,j),cnf=cnf,**kw)
                w.grid(row=i+1,column=j+1,sticky=Tkinter.W+Tkinter.E)
                w.configure(anchor=Tkinter.W)
                if width: w.configure(width=width[j+1])
                joint[-1].link(w.value)
            self.joint.append(joint)
    def _forward(self):
        value = self.value.get()
        for i in range(self.row):
            for j in range(self.column):
                if i >= len(value) or j >= len(value[0]):
                    self.joint[i][j].set_now(0)
                else:
                    self.joint[i][j].set_now(value[i][j])
                    
class Button(Tkinter.Button):
    '''クリックすると登録したコールバックを起動する。コールバックは通常のTkinter.Buttonと同様にcommand=<method>オプションで指定できる。'''
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Button.__init__(self,master,cnf,**kw)
        self.value = core.Port(None)
        self.configure(command=lambda:self.value.set(self.value.get())) # ボタンへのコールバックを設定する
        
class ToggleButton(Tkinter.Button):
    def __init__(self,master=None,text=None,cnf={},**kw):
        Tkinter.Button.__init__(self,master,cnf,**kw)
        self.value = core.Port(0)
        self.configure(command=self._clicked)
        if not type(text) == str:
            self.configure(text=text[0])
            self.text = text
        else:
            self.configure(text=text)
    def _clicked(self):
        if (self.value.get() + 1) < len(self.text):
            value = self.value.get() + 1
        else:
            value = 0
        self.configure(text=self.text[value])
        self.value.set(value)

class TrigButton(Tkinter.Button):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Button.__init__(self,master,cnf,**kw)
        self.value = core.Port(None)
        self.configure(command=self._backward)
    def _backward(self):
        self.configure(state=Tkinter.DISABLED)
        self.value.set(None)
        self.configure(state=Tkinter.NORMAL)

class LatchButton(Tkinter.Button):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Button.__init__(self,master,cnf,**kw)
        self.value = core.Port(True); self.value.bind(self._forward)
        self.configure(command=self._backward)
    def _backward(self):
        self.configure(state=Tkinter.DISABLED)
        self.value.set(False)
    def _forward(self):
        if self.value.get():
            self.configure(state=Tkinter.NORMAL)
        else:
            self.configure(state=Tkinter.DISABLED)
        
class Radiobuttons(Tkinter.Frame,utils.gui.SyncVarPort):
    def __init__(self,master=None,modes=[],cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.var = v = Tkinter.StringVar()
        for text,key in modes: Tkinter.Radiobutton(self,text=text,variable=v,value=key,command=self._backward).pack(anchor=Tkinter.W)
        self.value = core.Port(None); self.value.bind(self._forward)
        
class Checkbutton(Tkinter.Frame,utils.gui.SyncVarPort):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.var = v = Tkinter.IntVar()
        Tkinter.Checkbutton(self,variable=v,command=self._backward).pack(anchor=Tkinter.W)
        self.value = core.Port(0).bind(self._forward)

#class Menu(Tkinter.Menu):
#    TYPE_CASCADE, TYPE_ITEM = range(2)
#    ITEMS = []
#    def __init__(self,master=None,cnf={},**kw):
#        Tkinter.Menu.__init__(self,master,cnf,**kw)
#        self.callback = []
#        self.make()
#    def make(self,items=None):
#        if not items: items = self.__class__.ITEMS
#        for child in items:
#            self.add_child(self,child)
#    def remove_empty_items(self,cascade):
#        length = cascade.len()
#        for index in range(length):
#            if cascade.type(index) == 'cascade':
#                label = cascade.entrycget(index,'label')
#                menu  = cascade.nametowidget(cascade.entrycget(index,'menu'))
#                self.remove_empty_items(menu)
#                if utils.isfamily(menu,ChildrenMenu):
#                    continue
#                if menu.len() == 0:
#                    cascade.delete(index)
#    def itemtype(self,item):
#        cls = self.__class__
#        if len(item) == 1: return cls.TYPE_CASCADE
#        if type(item[1]) == list: return cls.TYPE_CASCADE
#        if repr(type(item[1])) == '<type \'classobj\'>': return cls.TYPE_CASCADE
#        if type(item[1]) == dict: return cls.TYPE_ITEM
#    def parse_cascade(self,item):
#        if len(item) == 1: return item[0], None
#        if type(item[1]) == list: return item[0], item[1:]
#        if repr(type(item[1])) == '<type \'classobj\'>': return item[0], item[1]
#    def add_child(self,parent,child):
#        def nocommand(command=None,**kw): return kw
#        cls = self.__class__
#        itemtype = self.itemtype(child) # child がどのような要素か調べる
#        if itemtype == cls.TYPE_CASCADE: # child が カスケード であるならば
#            label, item = self.parse_cascade(child) # label と item を抽出して
#            index = self.labeltoindex(label)
#            if index == None: # label が 不在 ならば
#                if not repr(type(item)) == '<type \'classobj\'>':
#                    cascade = Menu(parent,name=label.lower()) # あたらしいカスケード要素を生成して
#                    parent.add_cascade(label=label,menu=cascade)
#                    parent = cascade # 生成したカスケードを parent とする
#            else:
#                old = self.item(label)
#                if old == None: # old が カスケード でなければ
#                    self.delete(index) # 元の要素を削除して
#                    if not repr(type(item)) == '<type \'classobj\'>':
#                        cascade = Menu(parent,name=label.lower()) # 新しいカスケード要素で上書き
#                        parent.add_cascade(label=label,menu=cascade)
#                        parent = cascade
#                    else:
#                        pass
#                else:
#                    parent = old
#            if   item == None:
#                pass
#            elif repr(type(item)) == '<type \'classobj\'>':
#                parent.add_cascade(label=label,menu=item(parent,name=label.lower()))
#            elif type(item) == list:
#                for o in item:
#                    self.add_child(parent,o)
#        elif itemtype == cls.TYPE_ITEM:
#            name, kwargs = child
#            if kwargs.has_key('command'): # もしコマンドが定義されていて
#                if type(kwargs['command']) == str: # オペランドがメソッド名ならば
#                    command = getattr(self,kwargs['command']) # 自身のメソッドをコマンドに割り当てる
#                    getattr(parent,name)(command=command,**nocommand(**kwargs))
#                    return
#            getattr(parent,name)(**kwargs)
#    def assign(self,component):
#        self.comp = weakref.ref(component)
#        for key in self.children:
#            child = self.children[key]
#            if utils.functions.isfamily(child,Menu):
#                child.assign(component)
#    def component(self,path=None):
#        if not path: return self.comp()
#        ids = path.split('.')
#        child = self.comp()
#        for id in ids:
#            child = child.children[id]
#        return child
#    def labeltoindex(self,label):
#        index = 0
#        while index == self.index(index):
#            if label == self.entrycget(index,'label'):
#                return index
#            index = index + 1
#        return
#    def len(self):
#        index = 0
#        while index == self.index(index):
#            index = index + 1
#        return index
#    def item(self,label):
#        index = self.labeltoindex(label)
#        if not index: return
#        return self.nametowidget(self.entrycget(index,'menu'))

#class ChildrenMenu(Menu):
#    def assign(self,component):
#        Menu.assign(self,component)
#        self.update_children()
#    def update_children(self):
#        try: self.comp # もしコンポーネントが割り付けられていなければなにもしない
#        except AttributeError: return
#        component = self.component()
#        if component == None: # もしコンポーネントが廃棄されていれば割り付けを解除する
#            del self.comp
#            return
#        children = component.children.copy()
#        # メニューに存在する子Ｃが実在するかチェックしてメニューを削除する
#        existence = ['%s:%s' % (key,classname(children[key])) for key in children]
#        remove = []
#        for index in range(self.len()):
#            label = self.entrycget(index,'label')
#            flag = False
#            for s in existence:
#                if s == label:
#                    flag = True
#                    break
#            if not flag:
#                remove.append(index)
#        for index in remove:
#            self.delete(index)
#        # ツリーに存在する子Ｃがメニューアイテムに存在するかチェックしてメニューアイテムを追加する
#        for s in existence:
#            flag = False
#            for index in range(self.len()):
#                label = self.entrycget(index,'label')
#                if s == label:
#                    flag = True
#                    break
#            if flag: continue
#            self.add_command(label=s,command=partial(self.popup,label=s))
#        self.after(500,self.update_children)
#    def popup(self,label):
#        key = label.split(':')[0]
#        object = self.component(key)
#        #
#        tk = self
#        while tk: tk = tk.master
#        Layout.Application(Tkinter.Toplevel(tk),object,sync=False)
        
#class FileMenu(Menu):
#    ITEMS = []
#    RESTS = [
#             ['add_command', utils.kw(label='Config',command='popup_config')],
#             ['add_command', utils.kw(label='Console',command='popup_console')],
#             ]
#    def make_rest(self):
#        cls = self.__class__
#        if not self.len() == 0:
#            self.add_separator()
#        self.make(cls.RESTS)
#    def popup_config(self):
#        component = self.component()
#        if self.children.has_key('config'): return # すでにconfigを生成していなく
#        try: component.Config # componentにConfigクラスが存在していれば
#        except AttributeError: pass
#        else:
#            component.Config(master=Tkinter.Toplevel(self,name='config'),name='config').pack() # configパネルをポップアップする
#            self.children['config'].children['config'].assign(component)
#    def popup_console(self):
#        component = self.component()
#        if self.children.has_key('console'): return # すでにconsoleを生成していなく
#        try: component.Console # componentにConsoleクラスが存在していれば
#        except AttributeError: pass
#        else:
#            component.Console(master=Tkinter.Toplevel(self,name='console'),name='console').pack() # configパネルをポップアップする
#            self.children['console'].children['console'].assign(component)

#class DefaultMenu(Menu):
#    DEFAULT_ITEMS = [
#                     ['PyLAF', ],
#                     ['File', FileMenu],
#                     ['Edit'],
#                     ['Children', ChildrenMenu],
#                     ]
#    ITEMS = []
#    #RESTS = [
#    #         ['Window', ],
#    #         ['Help', ],
#    #         ]
#    # TODO:GUI毎に管理しなければならないパラメータの取り扱い。Componentからは初期値のみ管理。
#    def __init__(self,master=None,desc=[],cnf={},**kw):
#        cls = self.__class__
#        ITEMS = cls.ITEMS
#        cls.ITEMS = []
#        Menu.__init__(self,master,cnf,**kw)
#        self.make(cls.DEFAULT_ITEMS)
#        self.make(ITEMS)
#        self.make_rest(self.children)
#        self.remove_empty_items(self)
#    def make_rest(self,children):
#        #self.make(self.__class__.RESTS)
#        for key in children:
#            child = children[key]
#            if utils.isfamily(child,Menu):
#                try: make_rest = getattr(child,'make_rest')
#                except AttributeError: continue
#                make_rest()
#                self.make_rest(child.children)
                
class Thread(threading.Thread):
    EVENT_START, EVENT_CANCEL, EVENT_DONE,\
    STATE_DONE, STATE_COMPUTING, STATE_CANCELED, STATE_RUNNING = range(7)
    class StateCanceled(Exception): pass
    class SafeBuffer(Tkinter.Frame):
        def __init__(self,master=None,interval=200,cnf={},**kw):
            Tkinter.Frame.__init__(self,master,cnf,**kw)
            self.receive   = core.Port(None).bind(self._set)
            self.send      = core.Port(None)
            self.interval  = core.Port(interval)
            self._last     = None
            self._polling()
        def _set(self):
            self._last = self.receive.get()
        def _polling(self):
            if not self._last == None:
                self.send.set(self._last)
                self._last = None
            self.after(self.interval.get(),self._polling)
    class SafeQueue(Tkinter.Frame):
        def __init__(self,master=None,cnf={},**kw):
            Tkinter.Frame.__init__(self,master,cnf,**kw)
            self.receive = core.Port(None).bind(self._set)
            self.send    = core.Port(None)
            self._queue  = Queue.Queue()
            self._polling()
        def _set(self):
            self._queue.put(self.receive.get())
        def _polling(self):
            try:
                while 1:
                    self.send.set(self._queue.get_nowait())
            except Queue.Empty: pass
            self.after(200,self._polling)
    class LatchedTriggerButton(Tkinter.Button):
        def __init__(self,master=None,cnf={},**kw):
            Tkinter.Button.__init__(self,master,cnf,**kw)
            self.thread  = core.Port(None)
            self.remote  = core.Port(None).bind(self._forward)
            self._thread = threading.Thread(target=self._run)
            self._state  = False
            self.configure(command=self._backward)
        def _run(self):
            self.thread.set(Thread.EVENT_START)
            self.remote.set(Thread.EVENT_DONE)
        def _backward(self):
            if not self._state: self.activate()
            else              : self.deactivate()
        def _forward(self):
            remote = self.remote.get()
            if   remote == Thread.EVENT_DONE:   self.deactivate()
            elif remote == Thread.EVENT_START:  self.activate()
            elif remote == Thread.EVENT_CANCEL: self.deactivate()
        def activate(self):
            self.configure(state=Tkinter.DISABLED)
            self._state = True
            self._thread.start()
        def deactivate(self):
            self.configure(state=Tkinter.NORMAL)
            self._state = False
            self._thread = threading.Thread(target=self._run)
    class TriggerButton(Tkinter.Button):
        def __init__(self,master=None,text=['Waiting','Running'],cnf={},**kw):
            Tkinter.Button.__init__(self,master,cnf,**kw)
            self.thread  = core.Port(None)
            self.cancel  = core.Port(None)
            self.remote  = core.Port(None).bind(self._forward)
            self._thread = threading.Thread(target=self._run)
            self._state  = False
            self._text   = text
            self.configure(command=self._backward)
            self.configure(text=text[0])
        def _run(self):
            self.thread.set(Thread.EVENT_START)
            self.cancel.set(Thread.EVENT_DONE)
            self.remote.set(Thread.EVENT_DONE)
        def _backward(self):
            if not self._state: self.activate()
            else:
                self.cancel.set(Thread.EVENT_CANCEL)
                self.deactivate()
        def _forward(self,remote=None):
            if remote == None: remote = self.remote.get()
            if   remote == Thread.EVENT_DONE:  self.deactivate()
            elif remote == Thread.EVENT_START: self.activate()
            elif remote == Thread.EVENT_CANCEL:
                self.cancel.set(Thread.EVENT_CANCEL)
                self.deactivate()
        def activate(self):
            self.configure(text=self._text[1])
            self._state = True
            self._thread.setDaemon(True)
            self._thread.start()
            self.cancel.set(Thread.STATE_RUNNING)
        def deactivate(self):
            self.configure(text=self._text[0])
            self._state = False
            self._thread = threading.Thread(target=self._run)
        