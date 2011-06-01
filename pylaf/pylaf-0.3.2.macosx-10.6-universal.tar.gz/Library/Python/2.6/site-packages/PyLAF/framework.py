# coding: utf-8

import Tkinter, weakref, inspect

MASTER, SLAVE = range(2)

def chain_link(*comps):
    for i,c in enumerate(comps[:-1]): c.sig_out.link(comps[i+1].sig_in)

def iscontain(obj,cls):
    try:
        bases = inspect.getmro(obj.__class__) # オブジェクトのクラスツリーをタプルで返す
    except AttributeError:
        return False
    if bases.__contains__(cls):
        return True
    else:
        return False

def popcnf(key,cnf):
    item = None
    if cnf.has_key(key):
        item = cnf[key]
        del cnf[key]
    return item

class CallableList(list):
    '''
    関数を保持するリスト
    '''
    def call(self):
        for func in self:
            func()
# FuncList = CallableList

class SingletonList(list):
    '''
    同じアイテムをただひとつしか登録しないリスト
    '''
    def append(self,obj):
        if not self.__contains__(obj):
            list.append(self, obj)

class WeakRefList(list):
    '''
    オブジェクトの弱参照を保持するリスト
    '''
    def contains(self,obj):
        return self.tolist().__contains__(obj)
    def append(self,obj):
        if not self.contains(obj):
            list.append(self, weakref.ref(obj))
    def insert(self,index,obj):
        if not self.contains(obj):
            list.insert(self, index, weakref.ref(obj))
    def remove(self,obj):
        if self.contains(obj):
            for ref in self:
                if obj is ref():
                    list.remove(self, ref)
                    break
    def tolist(self):
        return [ref() for ref in self]
    def cleanup(self):
        '''
        dead参照のアイテムを削除する
        '''
        items = []
        for ref in self:
            if ref() == None:
                items.append(ref)
        for item in items:
            list.remove(self, item)

class CallableWeakRefList(WeakRefList):
    def call(self):
        for o in self: o()()

class Listner:
    def __init__(self,subject):
        self.subject = None
        self.register(subject)
    def register(self,subject,index=None):
        self.unregister()
        subject.register(self,index)
        self.subject = subject
    def unregister(self):
        if not self.subject == None:
            self.subject.unregister(self)
            self.subject = None
    def update(self,event): pass

class Subject:
    def __init__(self):
        self.listners = WeakRefList()
    def register(self,listner,index=None):
        if index == None:
            self.listners.append(listner)
        else:
            self.listners.insert(index,listner)
    def unregister(self,listner):
        self.listners.cleanup()
        self.listners.remove(listner)
    def notify(self,*args):
        self.listners.cleanup()
        for listner in self.listners.tolist(): listner.update(*args)

class Port(Listner):
    def __init__(self,variable):
        if variable.__class__ == Variable:
            raise FutureWarning('Port(Variable(value)) is going to obsolete.\n')
            Listner.__init__(self,variable)
            self._callbacks = CallableList()
        if iscontain(variable,Port):
            Listner.__init__(self,Variable(variable.get()))
            self._callbacks = CallableList()
            self.link(variable)
        else:
            Listner.__init__(self,Variable(variable))
            self._callbacks = CallableList()
        self._iscaller = False
    def update(self,*args):
        self._callbacks.call()
    def bind(self,func):
        self._callbacks.append(func)
        return self
    def link(self,*listners):
        for listner in listners:
            listner.subject.listners.cleanup()
            for obj in listner.subject.listners.tolist():
                obj.register(self.subject)
        return self
    def insertlink(self,index,listner):
        listner.subject.listners.cleanup()
        for obj in listner.subject.listners.tolist():
            obj.register(self.subject,index)
        return self
    def set(self,value,mode=MASTER):
        if not self._iscaller:
            self._iscaller = True
            self.subject.set(value,mode)
            self._iscaller = False
    def get(self):
        return self.subject.get()
    
class Variable(Subject):
    '''
    複数のPortクラスで同期する任意のリテラルを格納する実体クラス
    '''
    def __init__(self,value,**kw):
        Subject.__init__(self)
        self.value = None
        self.set(value,mode=SLAVE)
        # ==========================
        # for backward compatibility
        if kw.has_key('value'):
            self.set(kw['value'],mode=SLAVE)
            del kw['value']
        # ==========================
    def set(self,value,mode=MASTER):
        '''
        もしvalueがcopyメソッドを持っていればvalue.copy()する
        '''
        try:
            self.value = value.copy()
        except AttributeError:
            self.value = value
        if mode == MASTER:
            self.notify()
        else:
            self.notify_tk_only()
    def notify_tk_only(self,*args):
        self.listners.cleanup()
        for listner in self.listners.tolist():
            if iscontain(listner,VariableTk): listner.update(*args)
    def get(self):
        '''格納しているオブジェクトの参照を返す'''
        return self.value

class PortHolder:
    '''
    Portインスタンスをメンバとして保持する場合に発生する循環参照を自動的に解消する機構
    Portインスタンスをメンバとして保持するクラスはPortHolderを継承してdestroyメソッドでパージしなければならない
    '''
    def _inherit_ports(self,portholder,*ports,**kw):
        '''
        _inherit_ports(obj)
        _inherit_ports(obj,omit=[a,b,c])
        _inherit_ports(obj,a,b,c)
        '''
        m = inspect.getmembers(portholder,lambda x:iscontain(x,Port))
        #
        omit = []
        if kw.has_key('omit'): omit = kw['omit']
        #
        # print map(lambda x:x[0],m) # リストの第１引数だけをリストアップする
        ports = list(ports)
        if not ports == []:
            m = filter(lambda x:not ports.count(x[0]) == 0,m)
        else:
            m = filter(lambda x:omit.count(x[0]) == 0,m) # リストの第１引数がomitに含まれないものだけ選択する
        for name,info in m: setattr(self, name, getattr(portholder, name))
    def destroy(self):
        '''メンバからPortインスタンスへの参照を削除する'''
        m = inspect.getmembers(self,lambda x:iscontain(x,Port))
        for name,info in m: setattr(self, name, None)

class ComponentHolder:
    '''
    Component,FrameComponentインスタンスをメンバとして保持する場合に発生する循環参照を自動的に解消する機構
    '''
    def _remove(self,m):
        for name,info in m:
            if not name == 'master':
                setattr(self, name, None)
    def destroy(self):
        '''self.master以外のメンバからComponent,FrameCopmponentインスタンスへの参照を削除する'''
        self._remove(inspect.getmembers(self,lambda x:iscontain(x,LeafTk)))
        self._remove(inspect.getmembers(self,lambda x:iscontain(x,Tkinter.BaseWidget)))

class LeafTk:
    '''
    Tkinter.BaseWidgetのリーフになれるコンポーネント。Tkinter.pyを参考にした。
    '''
    def __init__(self,master):
        self.master = master
        self._name = repr(id(self))
        self._assign_to_master()
    def _assign_to_master(self):
        if self.master.children.has_key(self._name):
            '''master.childrenにおけるidの唯一性を保証する'''
            self.master.children[self._name].destroy()
        self.master.children[self._name] = self
    def _remove_from_master(self):
        '''master.childrenから自身へのオブジェクト参照を廃棄する'''
        if self.master.children.has_key(self._name):
            del self.master.children[self._name]
    def destroy(self):
        self._remove_from_master()
        
class Component(LeafTk,PortHolder,ComponentHolder):
    def __init__(self,master):
        LeafTk.__init__(self,master)
        self.children = {}
    def destroy(self):
        for c in self.children.values(): c.destroy() # purge children
        ComponentHolder.destroy(self) # purge component members
        PortHolder.destroy(self) # purge port members
        LeafTk.destroy(self) # purge itself
    def gui(self,master,cnf={},**kw):
        frm = Tkinter.Frame(master,cnf,**kw)
        Tkinter.Label(frm,text=self.__class__.__name__).pack(side=Tkinter.TOP,expand=1,fill=Tkinter.X)
        return frm
    def menu(self,master,cnf={},**kw):
        return None
    def link(self,sig_in,sig_out):
        sig_in.link(self.sig_in)
        sig_out.link(self.sig_out)
        return self

class Frame(Tkinter.Frame,PortHolder,ComponentHolder):
    def destroy(self):
        ComponentHolder.destroy(self)
        PortHolder.destroy(self)
        Tkinter.Frame.destroy(self)

class LabelFrame(Tkinter.LabelFrame,PortHolder,ComponentHolder):
    def destroy(self):
        ComponentHolder.destroy(self)
        PortHolder.destroy(self)
        Tkinter.LabelFrame.destroy(self)

class Equipment:
    def __init__(self,comp,gui=True,guicnf={}):
        if inspect.isclass(comp):
            self.component = comp(self)
        else:
            self.component = comp
        self._inherit_ports(self.component)
        if gui:
            self.gui = self.component.gui(self,**guicnf)
            self.gui.pack()
    def configure(self,gui=None):
        if not gui  == None:
            try:
                self.gui.destroy()
            except AttributeError: pass
            gui(self).pack()

class App(Frame,Equipment):
    def __init__(self,master,comp,gui=True,menu=True,guicnf={},cnf={},**kw):
        Frame.__init__(self,master,cnf,**kw)
        Equipment.__init__(self,comp,gui,guicnf)
        if menu:
            m = self.component.menu(self.master)
            if not m == None: self.master.config(menu=m)
    def configure(self,gui=None,menu=None,cnf={},**kw):
        Frame.configure(self,cnf,**kw)
        Equipment.configure(self,gui)
        if not menu == None: self.master.config(menu=menu(self.master))

class Embed(LabelFrame,Equipment):
    def __init__(self,master,comp,gui=True,menu=True,guicnf={},cnf={},**kw):
        LabelFrame.__init__(self,master,cnf,**kw)
        Equipment.__init__(self,comp,gui,guicnf)
        if menu: self.component.menu(self,popup=True)
    def configure(self,gui=None,menu=None,cnf={},**kw):
        Frame.configure(self,cnf,**kw)
        Equipment.configure(self,gui)
        if not menu == None: self.master.config(menu=menu(self,popup=True))

class VariableTk(Listner):
    '''
    Variableクラスを参照して同期するよう[Double|Int|String|Boolean]Varを拡張するMixin
    '''
    def __init__(self,port,forward=lambda x:x,backward=lambda x:x):
        Listner.__init__(self,port.subject)
        self.forward  = forward
        self.backward = backward
    def update(self,*args):
        self.set(self.forward(self.subject.get()))
    def fixed(self,*args):
        self.subject.set(self.backward(self.get()))
    def __eq__(self,other):
        return id(self) == id(other)

class DoubleVar(Tkinter.DoubleVar,VariableTk):
    def __init__(self,port,master=None,value=None,name=None,forward=lambda x:x,backward=lambda x:x):
        Tkinter.DoubleVar.__init__(self,master,forward(port.subject.get()),name)
        VariableTk.__init__(self,port,forward,backward)

class IntVar(Tkinter.IntVar,VariableTk):
    def __init__(self,port,master=None,value=None,name=None,forward=lambda x:x,backward=lambda x:x):
        Tkinter.IntVar.__init__(self,master,forward(port.subject.get()),name)
        VariableTk.__init__(self,port,forward,backward)
        
class StringVar(Tkinter.StringVar,VariableTk):
    def __init__(self,port,master=None,value=None,name=None,forward=lambda x:x,backward=lambda x:x):
        Tkinter.StringVar.__init__(self,master,forward(port.subject.get()),name)
        VariableTk.__init__(self,port,forward,backward)

class BooleanVar(Tkinter.BooleanVar,VariableTk):
    def __init__(self,port,master=None,value=None,name=None,forward=lambda x:x,backward=lambda x:x):
        Tkinter.BooleanVar.__init__(self,master,forward(port.subject.get()),name)
        VariableTk.__init__(self,port,forward,backward)
