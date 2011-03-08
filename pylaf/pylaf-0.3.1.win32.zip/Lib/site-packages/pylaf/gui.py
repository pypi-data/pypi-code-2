# coding: utf-8

import weakref, inspect, platform, types, re, functools, threading, Queue, time
import utils.gui, core, utils.functions
from functools import partial
from utils.gui.tkwidgets import *

class Entry(Tkinter.Entry):
    def __init__(self,master=None,format='%s',range=None,cnf={},**kw):
        Tkinter.Entry.__init__(self,master,cnf,**kw)
        self.format = format
        self.old = None
        self.range = range
        self.value = core.Port('').bind(self._forward)
        self.bind('<Escape>',self._forward) # ESCキーが押されたら値を破棄する
        self.bind('<Return>',self._backward) # RETURNキーが押されたら値を確定する
        self.bind('<FocusOut>',self._forward) # FOCUSが失われたら値を確定する
    def _forward(self,*args):
        self.delete(0,len(self.get()))
        self.insert(0,self.format % self.value.get())
    def _backward(self,*args):
        old = self.value.get()
        try: # 文字列を変換できればその値を
            new = type(self.value.get())(self.get())
        except ValueError: # できなければ零を代入する
            new = type(self.value.get())('0')
        if self.range:
            if not self.range(new): new = old # もし範囲に入っていなければ以前の値に戻す
        self.value.set(new) # Portで保持しているオブジェクト型に変換してセット

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
                joint.append(core.Port('').bind(functools.partial(self._backward,i=i,j=j)))
                w = Entry(self,name='item%d%d' % (i,j),format=format)
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
                    self.joint[i][j].set(0)
                else:
                    self.joint[i][j].set(value[i][j])
                    
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

class Menu(Tkinter.Menu):
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Menu.__init__(self,master,cnf,**kw)
        self._callbacks = {} # このカスケードに登録されているコールバックの辞書
    def add_sub(self,desc):
        label = desc[0]; type = desc[1]
        if type == 'command': # アイテム型がcommandだったら
            class Dummy: pass
            self._callbacks[label.lower()] = (weakref.ref(Dummy()),'') # label名で空のコールバックを登録し
            # Tkinterの仕様と合わせるため参照keyはlowercaseに統一する。
            self.add_command(label=label,command=partial(self._callback,key=label.lower())) # コールバックの起動メソッドを結合したアイテムを生成する。
    def _callback(self,key): # コールバックの起動メソッド
        try: cb = self._callbacks[key] # コールバックが存在していて
        except KeyError: return
        if not cb[0]() == None: # コールバックが生きていれば
            wobj, method = cb
            getattr(wobj(),method).__call__() # 起動する。
    def assign(self,key,x): # コールバックを登録する。
        if not x == utils.isfamily(x,core.Port):
            obj, name = x.__self__, x.__name__
            self._callbacks[key] = (weakref.ref(obj),name)

class MenuFactory(Tkinter.Menu):
    '''
    descに従ってメニューを生成する
    desc = [['Component',[‘Config', 'command']], # カスケードメニューラベル、最終メニューラベル、種類(command,toggleなど)
            ['Children', ['FGA', 'command')],
                         ['FGB', 'command')]]]
    '''
    DEFAULT_ITEMS = []
    DEFAULT_ASSIGNS = [] # [(child1, child2, ...), name, command]
    def __init__(self,master=None,desc=[],cnf={},**kw):
        Tkinter.Menu.__init__(self,master,cnf,**kw)
        #
        # デフォルトアイテムを追加する
        items = list(MenuFactory.DEFAULT_ITEMS)
        for item in desc:
            items.append(item)
        #desc.insert(0,['PyLAF', ['Kitchen','command']])
        #
        # アイテムを生成する
        for m in items: self.add_children(self,m) # descの最上位リストを巡回する
        #
        # デフォルトアサインリストを処理する
        for children,index,command in MenuFactory.DEFAULT_ASSIGNS:
            child = None
            for c in children:
                child = self.children[c]
            #child.entryconfig(index,command=command)
        #self.children['pylaf'].assign('kitchen',self.invoke_kitchen)
    def add_children(self,parent,children):
        if type(children[1]) == list: # サブメニューを持っていたら
            cascade = Menu(parent,name=children[0].lower()) # ラベルと同じ名前でchildrenに登録。名前はTkinterの制約からlowercaseに統一。
            parent.add_cascade(label=children[0],menu=cascade) # 上位に生成したカスケードを登録。
            for m in children[1:]: self.add_children(cascade,m) # サブメニューを巡回する
        else: # 最下層だったら
            parent.add_sub(children) # 上位のカスケードメニューに定義を渡して、メニューアイテムを生成する。

class ComponentWithGUI(core.Component,utils.gui.WithGUI):
    '''
    GUIを付随するコンポーネント
    ユーザコンポーネントを拡張する際のテンプレート
    destroy()が複数回実行されるのを避けるコードを含む
    '''
    def __init__(self,master=None,name=None):
        core.Component.__init__(self,master,name)
        utils.gui.WithGUI.__init__(self)
    def destroy(self):
        if self._dying: return # すできComponentWithGUI.destroy()を実行していなければ
        self._dying = True # 循環参照判別フラグを立て
        utils.gui.WithGUI.destroy(self)
        core.Component.destroy(self) # 下層のコンポーネントを破棄する
        
class Grid(Tkinter.Frame): # パネル構成のため、グリッド状にウィジェットを配置する
    # 複数のウィジェットを並べたい場合はFrameで固めて配置する
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.__geometry       = core.kw(sticky=Tkinter.W+Tkinter.E)
        self.__label_widget   = {}
        self.__label_geometry = core.kw(sticky=Tkinter.W+Tkinter.E)
    def append(self,widget,label=None,geometry={},label_widget={},label_geometry={}):
        '''
        widgetを最終行にgridする。labelが設定されていればラベル付きでウィジェットを配置する。
        ラベルのアクセスidはlabel+row(label0,label1,...)
        geometry:ウィジェット配置オプション。row,rowspan,column,columnspanは無効。
        label_widget：ラベル生成オプション。masterは無効。
        label_geometry:ラベル配置オプション。row,rowspan,column,columnspanは無効。
        '''
        def remove_options(kwargs,*options):
            for key in options:
                if kwargs.has_key(key):
                    del kwargs[key]
            return kwargs
        def update_options(default,custom):
            for key in custom: default[key] = custom[key]
            return default
        _geometry       = update_options(self.__geometry.copy(),      remove_options(geometry,'row','rowspan','column','columnspan'))
        _label_widget   = update_options(self.__label_widget.copy(),  remove_options(label_widget,'master'))
        _label_geometry = update_options(self.__label_geometry.copy(),remove_options(label_geometry,'row','rowspan','column','columnspan'))
        col,row = self.grid_size()
        if label:
            Tkinter.Label(self,text=label,name='label%d' % row,**_label_widget).grid(row=row,column=0,**_label_geometry)
            widget.grid(row=row,column=1,**_geometry)
        else:
            widget.grid(row=row,column=0,columnspan=2,**_geometry)
    
class Layout:
    class Embed(Tkinter.LabelFrame): # 埋め込み型のレイアウト。ラベルフレームで囲ってラベルを右クリックでポップアップメニュー。
        def __init__(self,master=None,cls=None,console=True,alignment='vertical',cnf={},**kw):
            Tkinter.LabelFrame.__init__(self,master,cnf,**kw)
            if alignment=='vertical':
                packw = {'side' : Tkinter.TOP}
            elif alignment=='horizontal':
                packw = {'side' : Tkinter.LEFT, 'anchor' : Tkinter.N}
            try: cls.Plot
            except AttributeError: pass
            else: cls.Plot(master=self,name='plot').pack(**packw)
            if console:
                try: cls.Console
                except AttributeError: pass
                else: cls.Console(master=self,name='console').pack(**packw)
            try: cls.Menu # clsがメニュークラスを保持していれば
            except AttributeError: pass # 用意されていなければなにもしない
            else:
                cls.Menu(master=self,name='menu')
                self.bind('<Control-Button-1>', self._rclicked) # Ctrl+右クリック
                if platform.system() == 'Darwin': # Darwinでは右クリックが異なる
                    self.bind('<Button-2>', self._rclicked) # DarwinだったらB2
                else:
                    self.bind('<Button-3>', self._rclicked) # Windows,LinuxだったらB3
        def _assign(self,comp,key):
            try: self.children[key].assign
            except (KeyError,AttributeError): pass
            else: self.children[key].assign(comp)
        def assign(self,comp):
            if comp == None: # もしコンポーネントが指定されていなければ
                class Dummy: pass
                self.comp = weakref.ref(Dummy()) # dead参照とするための捨てオブジェクトを参照
            else:
                self.comp = weakref.ref(comp) # コンポーネントを弱参照
            self._assign(comp,'plot')
            self._assign(comp,'console')
            self._assign(comp,'menu')
            return self
        def popup_config(self):
            if self.children.has_key('config'): return # すでにconfigを生成していなく
            try: self.comp().Config # componentにConfigクラスが存在していれば
            except AttributeError: pass
            else:
                self.comp().Config(master=Tkinter.Toplevel(self,name='config'),name='config').pack() # configパネルをポップアップする
                self.children['config'].children['config'].assign(self.comp())
            if self.children.has_key('console'): return # すでにconsoleを生成していなければ
            else:
                self.comp().Console(master=self.children['config'].children['config'],name='console').pack()
                self.children['config'].children['config'].children['console'].assign(self.comp())
        def _rclicked(self,e):
            self.children['menu'].tk_popup(e.x_root,e.y_root)
    class Application(Tkinter.Frame): # 親はToplevelかTkのどちらかでなければならない
        def __init__(self,master=None,klass=None,title=None,sync=True,pack=True,alignment='vertical',cnf={},**kw):
            Tkinter.Frame.__init__(self,master,cnf,**kw)
            
            if type(klass) == types.InstanceType:
                instance = klass
                klass = klass.__class__
                
            if alignment=='vertical':
                packw = {'side' : Tkinter.TOP}
            elif alignment=='horizontal':
                packw = {'side' : Tkinter.LEFT, 'anchor' : Tkinter.N}
                
            try: klass.Plot # プロットクラスが存在するか確認し
            except AttributeError: pass # 存在しなければなにもしない
            else: klass.Plot(master=self,name='plot').pack(**packw) # プロットパネルの生成
            
            try: klass.Console
            except AttributeError: pass # 用意されていなければなにもしない
            else: klass.Console(master=self,name='console').pack(**packw) # コンソールパネルの生成
            
            try: klass.Status
            except AttributeError: pass # 用意されていなければなにもしない
            else: klass.Status(master=self,name='status').pack() # ステータスパネルの生成
            
            try: klass.Menu
            except AttributeError: pass # 用意されていなければなにもしない
            else: self.master.config(menu=klass.Menu(master=self,name='menu')) # メニューを生成する
            
            self._sync  = sync # コンポーネントと寿命を同期する場合はTrue
            self._dying = False # 循環実行回避用フラグ
            
            # 後処理
            try: instance # もしklass引き数にインスタンスが設定されていれば
            except UnboundLocalError: pass
            else: self.assign(instance) # インスタンスを割り当てる
            if title: self.master.title(title) # タイトル引き数に応じてタイトルを設定する
            if pack: self.pack() # パック引き数に応じてパックする
        def assign(self,comp):
            if comp == None: # もしコンポーネントが指定されていなければ
                class Dummy: pass
                self.comp = weakref.ref(Dummy()) # dead参照とするための捨てオブジェクトを参照
            else:
                self.comp = weakref.ref(comp) # コンポーネントを弱参照
                comp._guis[repr(id(self))] = self # gui寿命同期用弱参照辞書へ登録
            c = self.children
            
            try: c['plot'].assign
            except (KeyError,AttributeError): pass
            else: c['plot'].assign(comp) # コールバックやポートを結合する
            
            try: c['console'].assign
            except (KeyError,AttributeError): pass
            else: c['console'].assign(comp)
            
            try: c['status'].assign
            except (KeyError,AttributeError): pass
            else: c['status'].assign(comp)
            
            try: c['menu'].assign
            except (KeyError,AttributeError):pass
            else: c['menu'].assign(comp)
            
            return self
        def popup_config(self):
            if self.children.has_key('config'): return # すでにconfigを生成していなく
            try: self.comp().Config # componentにConfigクラスが存在していれば
            except AttributeError: pass
            else:
                self.comp().Config(master=Tkinter.Toplevel(self,name='config'),name='config').pack() # configパネルをポップアップする
                self.children['config'].children['config'].assign(self.comp())
        def destroy(self):
            if self._dying: return # Application.destroy()を最初に実行するのならば
            self._dying = True # 循環参照判別フラグを立て
            try: self.comp
            except AttributeError:
                Tkinter.Frame.destroy(self)
                return
            comp = self.comp()
            if not comp == None: # コンポーネントが存在して
                if self._sync: # 寿命同期スイッチがTrueであり
                    if comp._dying == True: # コンポーネント側からの呼び出しならば
                        #if self.master.children.has_key(self._name): del self.master.children[self._name] # 再呼び出しを防止し（不要？）
                        self.master.destroy() # Toplevelを削除する
                    else: # destroy元がGUI側ならば
                        comp.destroy() # コンポーネントのdestroy()メソッドをコールする。
            Tkinter.Frame.destroy(self) # 下層のウィジェットを破棄する
            
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
        
if __name__ == '__main__':
    class BasicSample(ComponentWithGUI): # フレームワークの基本機能を使ったGUIの構築例
        class Console(Grid):
            def __init__(self,master=None,cnf={},**kw):
                Grid.__init__(self,master,cnf={},**kw)
                self.append(Entry(self,name='param1'),label='A =')
                self.append(Label(self,name='param2'),label='2 x A =',label_geometry=core.kw(sticky=Tkinter.E))
                self.append(WeakValuedButton(self,name='callback',text='callback'))
                self.append(WeakValuedButton(self,name='destroy',text='destroy'))
                self.append(Tkinter.Button(self,name='cwtest',text='cwtest'))
                self.append(Tkinter.Button(self,name='rebind',text='rebind',command=core.CallWrapper(self._rebind)))
            def assign(self,component):
                self.children['param1'].value.set(component.param1.get())
                component.param1.link(self.children['param1'].value)
                self.children['param2'].value.set(component.param2.get())
                component.param2.link(self.children['param2'].value)
                self.children['callback'].configure(command=component.cb1)
                self.children['destroy'].configure(command=component.destroy)
                #self.children['cwtest'].configure(command=component.cb1) # 直接バインドするとコンポーネントが解放されない
                self.children['cwtest'].configure(command=core.CallWrapper(component.cb1))
            def _rebind(self):
                # self.children['destroy'].click() # <- こんな感じで操作できるといいね
                self.assign(BasicSample(core.Root()))
        def __init__(self,master=None,name=None):
            ComponentWithGUI.__init__(self,master,name)
            self.param1 = core.Port(1.); self.param1.bind(self.calc)
            self.param2 = core.Port(0.)
        def calc(self): # parm1に結合されたコールバック
            self.param2.set(2 * self.param1.get())
        def cb1(self): # とりあえず、何にも結合されていないコールバック
            print 'alive'
            
    tk = Tkinter.Tk()
    basic = Layout.Application(tk,BasicSample(core.Root()),title='basic sample',sync=False)
    Tkinter.mainloop()
    basic = weakref.ref(basic)
    print 'basic:', basic
