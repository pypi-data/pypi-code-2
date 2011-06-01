# coding: utf-8

import weakref, types, inspect, platform, types, numpy
import Tkinter
import ttk #@UnresolvedImport
import core, widgets, utils
from functools import partial

def limit_depth(map,depth=None):
    if not depth == None:
        remove = []
        for key in map:
            if len(key.split('.')) > depth:
                remove.append(key)
        for key in remove:
            del map[key]
    return map

def pathtoid(path):
    if len(path) == 0: return ''
    id = path[0]
    for s in path[1:]:
        id = '%s.%s' % (id,s)
    return id

def classname(obj): return repr(obj.__class__).split('.')[-1].split(' ')[0]

def widget(object,id):
    path   = id.split('.')
    def mycore(parent):
        children = parent.children
        for key in children:
            child = parent.children[key]
            if utils.isfamily(child,BasePanel): continue # パネルに到達したら別の枝を探索
            if not key == path[0]: # 名前が一致しなければ
                target = mycore(child) # さらに探索する
                if target == None:
                    continue
                else:
                    return target
            ports = inspect.getmembers(child,core.isPort)
            if not len(ports) == 0: # 名前が一致してかつPyLAFウィジェットならば
                path.pop(0) # 探索パスを１段深くして
                if len(path) == 0: return child # 最終段であれば child が対象
                target = mycore(child)
                if target == None:
                    continue
                else:
                    return target
    return mycore(object)

def console(self,path=None):
    '''
    配下のコンソールを取得する（コンソール以外のウィジェットは無視する）
    ワイルドカード * が与えられた場合は、最初に見つかったコンソールを返す
    pathが与えられなかった場合は、最初に見つかったコンソールを返す
    もしコンソールが見つからなければ None を返す
    '''
    if path == None:
        path = ['*']
    else:
        path = path.split('.')
    def mycore(parent):
        for key in parent.children:
            child = parent.children[key]
            if not utils.isfamily(child,BaseConsole): # もしconsoleでなければ
                target = mycore(child) # さらに探索し
                if target == None:
                    continue # 見つからなければ別のブランチを探索する
                else:
                    return target # 見つかればtargetを返す
            if path[0] == '*': # ワイルドカードならば
                return child # childを返す
            if key == path[0]: # もし名前が一致すれば
                path.pop(0) # 探索パスを１段深くして
                if len(path) == 0: return child # 最終段であれば child が対象
                target = mycore(child) # 最終段でなければさらに探索を続ける
                if target == None:
                    continue
                else:
                    return target
            # 一致しなければ探索を打ち切り別のブランチを検索する
    return mycore(self)
    
class Layout:
    '''
    Panelの配置とコンポーネント割付を管理する
    '''
    def available_panels(self):
        '''
        直下のすべてのパネルを格納した辞書を返す
        '''
        panels       = {}
        current_path = []
        def core(parent):
            for key in parent.children:
                child = parent.children[key]
                if utils.isfamily(child, BaseConsole): # Consoleを見つけたら探索を打ち切る
                    continue
                if utils.isfamily(child, BasePanel): # Panelを見つけたらパスの末尾にキーを追加したうえで辞書に追加
                    current_path.append(key)
                    panels[pathtoid(current_path)] = child
                core(child)
                if utils.isfamily(child, BasePanel): # Panelから離脱する場合はパスの末尾を削除する
                    current_path.pop(-1)
        core(self)
        return panels
    def panel(self,id):
        panels = self.available_panels()
        if panels.has_key(id):
            return panels[id]
        else:
            return
    # TODO: core.PortでSubjectへ同一ポートやコールバックを複数回登録しないように変更すること
    # TODO: linkmapをどこで設定するのか．．．？
    # TODO: assignmapをどこで設定するべきか検討する
    def component(self,path=None):
        return self.comp().component(path)
    def assign(self,component):
        self.comp = weakref.ref(component)
        available_panels = limit_depth(self.available_panels(),depth=1)
        for key in available_panels: # デフォルトではカレントコンポーネントを割り振る
            self.panel(key).assign(component)
    def popup_config(self,master,**kw):
        component = self.component()
        try: component.Config
        except AttributeError: return
        notebook = ttk.Notebook(master,name='config',**kw)
        notebook.pack(expand=True,fill=Tkinter.X)
        panels = inspect.getmembers(component.Config,inspect.isclass)
        subpanels = []
        for name,klass in panels:
            panel = klass(notebook,name=name.lower())
            subpanels.append(panel)
            notebook.add(panel,text=name)
        return subpanels
        
class Standard(Tkinter.Frame,Layout):
    def __init__(self,master=None,klass=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        try: klass.Plot
        except AttributeError: pass
        else:
            klass.Plot(self,name='plot').grid(row=1,column=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
            self.grid_rowconfigure(1,weight=1)
        try: klass.Control
        except AttributeError:
            control = ControlPanelBuilder(self,klass,name='control')
        else:
            control = klass.Control(self,name='control')
        control.grid(row=2,column=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
        #self.grid_rowconfigure(2,weight=1)
        try: klass.Status
        except AttributeError: pass
        else:
            klass.Status(self,name='status').grid(row=3,column=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
            #self.grid_rowconfigure(3,weight=1)
        try: klass.Toolbar
        except AttributeError: pass
        else:
            klass.Toolbar(self,name='toolbar').grid(row=0,column=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
            #self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        
class StandardH(Tkinter.Frame,Layout):
    def __init__(self,master=None,klass=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        try: klass.Plot
        except AttributeError: pass
        else:
            klass.Plot(self,name='plot').grid(row=1,column=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
            self.grid_rowconfigure(1,weight=1)
        try: klass.Control
        except AttributeError:
            control = ControlPanelBuilder(self,klass,name='control')
        else:
            control = klass.Control(self,name='control')
        control.grid(row=1,column=1,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
        #self.grid_rowconfigure(1,weight=1)
        try: klass.Status
        except AttributeError: pass
        else:
            klass.Status(self,name='status').grid(row=2,column=0,columnspan=2,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
            #self.grid_rowconfigure(2,weight=1)
        try: klass.Toolbar
        except AttributeError: pass
        else:
            klass.Toolbar(self,name='toolbar').grid(row=0,column=0,columnspan=2,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
            #self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
        
class PlotLayout(Tkinter.Frame,Layout):
    def __init__(self,master=None,klass=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        klass.Plot(self,name='plot').pack(expand=True,fill=Tkinter.BOTH)
    def popup_config(self,master,**kw):
        component = self.component()
        try: component.Config
        except AttributeError:
            try: component.Control
            except AttributeError: return
        notebook = ttk.Notebook(master,name='config',**kw)
        notebook.pack(expand=True,fill=Tkinter.X)
        subpanels = []
        try: component.Config
        except AttributeError: pass
        else:
            panels = inspect.getmembers(component.Config,inspect.isclass)
            for name,klass in panels:
                panel = klass(notebook,name=name.lower())
                subpanels.append(panel)
                notebook.add(panel,text=name)
        try: component.Control
        except AttributeError:
            panel = ControlPanelBuilder(self,component.__class__,name='control')
        else:
            panel = component.Control(notebook,name='control')
        subpanels.append(panel)
        notebook.add(panel,text='Control')
        return subpanels
        
class ControlLayout(Tkinter.Frame,Layout):
    def __init__(self,master=None,klass=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        try: klass.Control
        except AttributeError:
            control = ControlPanelBuilder(self,klass,name='control')
        else:
            control = klass.Control(self,name='control')
        control.pack(expand=True,fill=Tkinter.X)
        
class TableBuilder:
    def __init__(self,master,column=2):
        self.master = weakref.ref(master)
        self.column = column
        col, row    = master.grid_size()
        self.cursor = (0, row)
    def add(self,klass,*args,**kwargs):
        self._item = weakref.ref(klass(self.master(),*args,**kwargs))
        return self
    def grid(self,row=None,column=None,rowspan=None,columnspan=1,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S,**kwargs):
        # rowspan は無視
        column, row = self.cursor
        self._item().grid(row=row,column=column,columnspan=columnspan,sticky=sticky,**kwargs)
        #self.master().grid_rowconfigure(row,weight=1)
        self.master().grid_columnconfigure(column,weight=1)
        if (column + columnspan) <= (self.column - 1):
            column = column + columnspan
        else:
            column = 0
            row = row + 1
        self.cursor = (column, row)
        return self
    def item(self):
        return self._item()
    def bind(self,*args,**kwargs):
        return self.item().bind(*args,**kwargs)
        
class BasePanel:
    '''
    パネルの生成
        ウィジェットの配置
        コンソールの配置
    コンポーネントをアサインする
    '''
    def available_panels(self):
        '''
        直下のすべてのパネルを格納した辞書を返す
        '''
        panels       = {}
        current_path = []
        def core(parent):
            for key in parent.children:
                child = parent.children[key]
                if utils.isfamily(child, BaseConsole): # Consoleを見つけたら探索を打ち切る
                    continue
                if utils.isfamily(child, BasePanel): # Panelを見つけたらパスの末尾にキーを追加したうえで辞書に追加
                    current_path.append(key)
                    panels[pathtoid(current_path)] = child
                core(child)
                if utils.isfamily(child, BasePanel): # Panelから離脱する場合はパスの末尾を削除する
                    current_path.pop(-1)
        core(self)
        return panels
    def available_consoles(self):
        '''
        配下のすべてのコンソールを格納した辞書を返す
        '''
        consoles     = {}
        current_path = []
        def core(parent):
            for key in parent.children:
                child = parent.children[key]
                if utils.isfamily(child, BaseConsole):
                    current_path.append(key)
                    consoles[pathtoid(current_path)] = child
                    current_path.pop(-1)
                else:
                    core(child)
        core(self)
        return consoles
    def port(self,id):
        path = id.split('.')
        path, name = path[:-1], path[-1]
        def myport(object,name):
            try: port = getattr(object,name)
            except AttributeError: # メンバが存在しなくて
                #children = object.children
                #print name, children
                child = widget(object,name)
                #if not children.has_key(name): return # 子ウィジェットがなければ None
                #child = children[name]
                if child == None: return # 子ウィジェットがなければ None
                try: default = getattr(child,'sig_in')
                except AttributeError: pass
                try: default = getattr(child,'sigin')
                except AttributeError: pass
                try: default = getattr(child,'value')
                except AttributeError: pass
                try: default # デフォルトポートがあるか調べて
                except AttributeError: return # 存在しなければ None
                port = default # ポートをデフォルトポートに設定する
            if not core.isPort(port): return # ポートオブジェクトでなければ None
            return port
        def mycore(parent): # descent path
            if len(path) == 0: return myport(parent,name)
            children = parent.children
            child_name = path[0]
            if not children.has_key(child_name): return # オブジェクトが存在しなければ None
            path.pop(0)
            mycore(children[child_name])
        return mycore(self)
    def available_ports(self):
        '''
        自身の配下で到達可能なすべてのポートマップを探索して返す
        同一のパス名で到達可能なポートが複数ある場合、以下の優先順位で上位のポートをマップする
        優先順位：
            [widget_name...]portname
            [widget_name...]widget_name（暗黙にプライマリーポートを指定）
            プライマリーポートの優先順位
                'value', 'sigin', 'sig_in'
        '''
        #map = {}
        map = weakref.WeakValueDictionary()
        # ウィジェットの保有するポートを探索する
        available_widgets = self.available_widgets()
        for available_widget_path in available_widgets:
            #available_widget = self.widget(available_widget_path) # ボトルネックだった
            available_widget = available_widgets[available_widget_path] # 高速化のため
            #members = inspect.getmembers(available_widget,lambda x:utils.functions.isfamily(x,core.Port))
            members = inspect.getmembers(available_widget,core.isPort)
            prime = {}
            for name,port in members:
                map['%s.%s' % (available_widget_path,name)] = port
                if   name == 'value':  prime[name] = port
                elif name == 'sigin':  prime[name] = port
                elif name == 'sig-in': prime[name] = port
            if   prime.has_key('value'):  map[available_widget_path] = prime['value']
            elif prime.has_key('sigin'):  map[available_widget_path] = prime['sigin']
            elif prime.has_key('sig-in'): map[available_widget_path] = prime['sig-in']
        # パネルの保有するポートを探索する
        #members = inspect.getmembers(self,lambda x:utils.functions.isfamily(x,core.Port))
        members = inspect.getmembers(self,core.isPort)
        for name,port in members:
            map[name] = port
        return map
    #
    # 配下のウィジェットからポートを保有するものだけを選んで論理パスをキーとした辞書を返す
    def available_widgets(self):
        widgets = {}
        currentpath = []
        def pathtoid(path):
            if len(path) == 0: return ''
            id = path[0]
            for s in path[1:]:
                id = '%s.%s' % (id,s)
            return id
        def mycore(parent):
            for key in parent.children:
                child = parent.children[key]
                if utils.isfamily(child,BasePanel):
                    continue
                #ports = inspect.getmembers(child,lambda x:utils.isfamily(x,core.Port))
                ports = inspect.getmembers(child,core.isPort)
                if not len(ports) == 0:
                    currentpath.append(key)
                    widgets[pathtoid(currentpath)] = child
                mycore(child)
                if not len(ports) == 0:
                    currentpath.pop(-1)
        mycore(self)
        return widgets
    console = console
    #def console(self,id):
    #    consoles = self.available_consoles()
    #    if consoles.has_key(id):
    #        return consoles[id]
    #    else:
    #        return
    def clear_portcache(self):
        try: self.ports
        except AttributeError: return
        del self.ports
    def port_old(self,id):
        '''
        自身の配下のpathで指定されるポートを返す
        注意！：最初に呼ばれたときにキャッシュを生成するので
              ウィジェット構造が確定してから利用すること
        　　　　ウィジェット構造が変化した場合はclear_portcacheを実行してください
        path:
            書式１：[widget_name...]portname
            書式２：[widget_name...]widget_name（暗黙にプライマリーポートを指定）
            到達可能な複数のポートが存在する場合は書式１、２の順で優先適用する
        もし存在しなければNoneを返す
        '''
        try: self.ports
        except AttributeError:
            self.ports = self.available_ports()
        if self.ports.has_key(id):
            return self.ports[id]
        else:
            return
    def widget(self,id):
        widgets = self.available_widgets()
        if widgets.has_key(id):
            return widgets[id]
        else:
            return
    def assign_panel(self,component):
        '''
        直近の配下パネルへのアサイン
        '''
        available_panels = limit_depth(self.available_panels(),depth=1)
        for key in available_panels:
            available_panels[key].assign(component)
    def assign_console(self,component):
        '''
        直近の配下コンソールへのアサイン
        '''
        # map: 対応関係を格納する辞書 'コンソールパス' : 'コンポーネントパス'
        map = {}
        # 優先順位２：同一パスのコンポーネント
        for console_name in limit_depth(self.available_consoles(),depth=1):
            map[console_name] = console_name
        # 優先順位１：assignmap
        try: self.assignmap
        except AttributeError: pass
        else:
            for console_path in self.assignmap:
                component_path = self.assignmap[console_path]
                if not len(console_path.split('.')) == 1:
                    map[console_path] = component_path
        # mapに従ってcomponentをconsoleへassignする
        for console_path in map:
            component_path = map[console_path]
            child          = component.child(component_path)
            console        = self.console(console_path)
            if child == None: # もし対象となるコンポーネントが存在しなければ匿名で生成する
                component_name = component_path.split('.')[-1]
                child = console.klass(component)# ,name=component_name)
                console.sync_on()
                # 親コンポーネントのsigoutとsiginをバインドする
                try: component.sig_out
                except AttributeError: pass
                else: src = component.sig_out
                try: component.sigout
                except AttributeError: pass
                else: src = component.sigout
                try: src
                except NameError: continue
                #
                try: child.sig_in
                except AttributeError: pass
                else: dst = child.sig_in
                try: child.sigin
                except AttributeError: pass
                else: dst = child.sigin
                try: dst
                except NameError: continue
                src.link(dst)
            console.assign(child)
    def assign(self,component):
        '''
        コンポーネントをアサインする
        componentは事前に存在していなければならない
        '''
        self.assign_panel(component)   # 直近の配下パネルへのアサイン
        self.assign_console(component) # 直近の配下コンソールへのアサイン
        '''
        ポートをリンクする
        '''
        # map: 対応関係を格納する辞書 'ターゲットポートパス' : 'ソースポートパス'
        map = {}
        # 優先順位２：同一パスのコンポーネントのポート
        for target_path in self.available_ports(): # 配下のすべてのポートが対象
            # Component 以外が与えられた場合、単純な参照を行う（ControlPanelBuilderのために）
            try: component.port
            except AttributeError:
                try: getattr(component,target_path)
                except AttributeError: pass
                else: map[target_path] = target_path
            else:
                if not component.port(target_path) == None: # リンク対象が存在していれば
                    map[target_path] = target_path
        # 優先順位１：linkmap
        try: self.linkmap
        except AttributeError: pass
        else:
            for target_path in self.linkmap:
                source_path = self.linkmap[target_path]
                if source_path == None:
                    del map[target_path] # source_path が None ならリンク取り消し
                else:
                    map[target_path] = source_path
                #component.port(source_path).link(self.port(target_path),set=True)
        #     配下のポートを保有するウィジェット（パネルとコンソールを除く）すべてを対象にリンクする
        #         1) linkmap
        #             getattr(component.child(path),name).link(getattr(self.widget(path),name),set=True)
        #         2) 同一名のコンポーネントのポート
        #             getattr(component,name).link(getattr(self.widget(path),name),set=True)
        #     自身の保有するすべてのポートを対象にリンクする
        #         1) linkmap
        #             getattr(component.child(path),name).link(getattr(self,name),set=True)
        #         2) 同一名のコンポーネントのポート
        #             getattr(component,name).link(getattr(self,name),set=True)
        # print component, self.__class__, map
        # mapに従ってportをcomponentのportへlinkする
        for target_path in map:
            source_path = map[target_path]
            self.port(target_path).disable(self)
            # Component 以外が与えられた場合、単純参照をおこなう
            try: component.port
            except AttributeError:
                getattr(component,source_path).link(self.port(target_path),set=True)
            else:
                component.port(source_path).link(self.port(target_path),set=True)
            #
            self.port(target_path).enable()
            # 複数のポートを対象にするならば次のコードだが、setのところでパフォーマンス上の問題が予期されるので不採用
            #source_paths = map[target_path]
            #if type(source_paths) == str:
            #    source_paths = (source_paths)
            #for source_path in source_paths:
            #    component.port(source_path).link(self.port(target_path),set=True)
    def sibling(self,path):
        ''' 兄弟パネルを取得する '''
        return self.layout().panel(path)
    def layout(self):
        ''' 直近の上位レイアウトを取得する '''
        master = self.master
        while not utils.isfamily(master,Layout):
            master = master.master
        return master
    def component(self,path=None):
        return self.layout().component(path)
        
class Panel(Tkinter.Frame,BasePanel): pass

class ControlPanelBuilder(Panel):
    def __init__(self,master=None,klass=None,cnf={},**kw):
        Panel.__init__(self,master,cnf,**kw)
        # klassにClassType以外が与えられた場合、インスタンスが与えられたものとして処理する
        #if type(klass) == types.ClassType:
        #    instance = klass()
        #    destroy  = True
        #else:
        #    instance = klass
        #    klass    = klass.__class__
        #    destroy  = False
        #
        instance = klass()
        builder = TableBuilder(self)
        members = inspect.getmembers(instance,core.isPort)
        for key,port in members:
            value = port.subject.value
            if (
                type(value) == types.NoneType or
                type(value) == types.InstanceType or
                type(value) == numpy.ndarray
                ): continue
            builder.add(Tkinter.Label,text=key).grid()
            builder.add(widgets.Entry,name=key).grid()
            #self.widget(key).bind('<Return>',self._trig)
        # もし、klassがClassTypeだった場合、生成したインスタンスを破棄する
        #if destroy: instance.destroy()
        #
        try: instance.destroy()
        except AttributeError: pass
    #def _trig(self,*args,**kwargs):
    #    component = self.layout().component()
    #    members = [key for key, port in inspect.getmembers(component,core.isPort)]
    #    if   members.count('sigout'):  component.sigout.get()
    #    elif members.count('sig_out'): component.sig_out.get()
        
class Menu(Tkinter.Menu):
    TYPE_CASCADE, TYPE_ITEM = range(2)
    ITEMS = []
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Menu.__init__(self,master,cnf,**kw)
        self.callback = []
        self.make()
    def make(self,items=None):
        if not items: items = self.__class__.ITEMS
        for child in items:
            self.add_child(self,child)
    def remove_empty_items(self,cascade):
        length = cascade.len()
        for index in range(length):
            if cascade.type(index) == 'cascade':
                label = cascade.entrycget(index,'label')
                menu  = cascade.nametowidget(cascade.entrycget(index,'menu'))
                self.remove_empty_items(menu)
                if utils.isfamily(menu,ChildrenMenu):
                    continue
                if menu.len() == 0:
                    cascade.delete(index)
    def itemtype(self,item):
        cls = self.__class__
        if len(item) == 1: return cls.TYPE_CASCADE
        if type(item[1]) == list: return cls.TYPE_CASCADE
        if repr(type(item[1])) == '<type \'classobj\'>': return cls.TYPE_CASCADE
        if type(item[1]) == dict: return cls.TYPE_ITEM
    def parse_cascade(self,item):
        if len(item) == 1: return item[0], None
        if type(item[1]) == list: return item[0], item[1:]
        if repr(type(item[1])) == '<type \'classobj\'>': return item[0], item[1]
    def add_child(self,parent,child):
        def nocommand(command=None,**kw): return kw
        cls = self.__class__
        itemtype = self.itemtype(child) # child がどのような要素か調べる
        if itemtype == cls.TYPE_CASCADE: # child が カスケード であるならば
            label, item = self.parse_cascade(child) # label と item を抽出して
            index = self.labeltoindex(label)
            if index == None: # label が 不在 ならば
                if not repr(type(item)) == '<type \'classobj\'>':
                    cascade = Menu(parent,name=label.lower()) # あたらしいカスケード要素を生成して
                    parent.add_cascade(label=label,menu=cascade)
                    parent = cascade # 生成したカスケードを parent とする
            else:
                old = self.item(label)
                if old == None: # old が カスケード でなければ
                    self.delete(index) # 元の要素を削除して
                    if not repr(type(item)) == '<type \'classobj\'>':
                        cascade = Menu(parent,name=label.lower()) # 新しいカスケード要素で上書き
                        parent.add_cascade(label=label,menu=cascade)
                        parent = cascade
                    else:
                        pass
                else:
                    parent = old
            if   item == None:
                pass
            elif repr(type(item)) == '<type \'classobj\'>':
                parent.add_cascade(label=label,menu=item(parent,name=label.lower()))
            elif type(item) == list:
                for o in item:
                    self.add_child(parent,o)
        elif itemtype == cls.TYPE_ITEM:
            name, kwargs = child
            if kwargs.has_key('command'): # もしコマンドが定義されていて
                if type(kwargs['command']) == str: # オペランドがメソッド名ならば
                    command = getattr(self,kwargs['command']) # 自身のメソッドをコマンドに割り当てる
                    getattr(parent,name)(command=command,**nocommand(**kwargs))
                    return
            getattr(parent,name)(**kwargs)
    def assign(self,component):
        self.comp = weakref.ref(component)
        for key in self.children:
            child = self.children[key]
            if utils.functions.isfamily(child,Menu):
                child.assign(component)
    def component(self,path=None):
        if not path: return self.comp()
        ids = path.split('.')
        child = self.comp()
        for id in ids:
            child = child.children[id]
        return child
    def labeltoindex(self,label):
        index = 0
        while index == self.index(index):
            try: self.entrycget(index,'label')
            except: pass
            else:
                if label == self.entrycget(index,'label'):
                    return index
            index = index + 1
        return
    def len(self):
        index = 0
        while index == self.index(index):
            index = index + 1
        return index
    def item(self,label):
        index = self.labeltoindex(label)
        if not index: return
        return self.nametowidget(self.entrycget(index,'menu'))

class ChildrenMenu(Menu):
    def assign(self,component):
        Menu.assign(self,component)
        self.update_children()
    def update_children(self):
        try: self.comp # もしコンポーネントが割り付けられていなければなにもしない
        except AttributeError: return
        component = self.component()
        if component == None: # もしコンポーネントが廃棄されていれば割り付けを解除する
            del self.comp
            return
        # Component 以外が与えられた場合の処理
        try: component.children
        except AttributeError: return
        #
        children = component.children.copy()
        # メニューに存在する子Ｃが実在するかチェックしてメニューを削除する
        existence = ['%s:%s' % (key,classname(children[key])) for key in children]
        remove = []
        for index in range(self.len()):
            try:
                label = self.entrycget(index,'label')
            except: continue
            flag = False
            for s in existence:
                if s == label:
                    flag = True
                    break
            if not flag:
                remove.append(index)
        for index in remove:
            self.delete(index)
        # ツリーに存在する子Ｃがメニューアイテムに存在するかチェックしてメニューアイテムを追加する
        for s in existence:
            flag = False
            for index in range(self.len()):
                try:
                    label = self.entrycget(index,'label')
                except: continue
                if s == label:
                    flag = True
                    break
            if flag: continue
            self.add_command(label=s,command=partial(self.popup,label=s))
        self.after(500,self.update_children)
    def popup(self,label):
        key = label.split(':')[0]
        object = self.component(key)
        #
        tk = self
        while tk: tk = tk.master
        Console(Tkinter.Toplevel(tk),object,sync=False)
        
class FileMenu(Menu):
    ITEMS = []
    RESTS = [
             ['add_command', utils.kw(label='Config',command='popup_config')],
             ]
    def make_rest(self):
        cls = self.__class__
        if not self.len() == 0:
            self.add_separator()
        self.make(cls.RESTS)
    def popup_config(self):
        if self.children.has_key('config'): return # すでにconfigを生成していなければ
        component = self.component()
        console = self
        while not utils.isfamily(console,BaseConsole):
            console = console.master
        layout   = console.layout()
        toplevel = Tkinter.Toplevel(layout,name='config')
        panels = layout.popup_config(toplevel)
        if panels == None:
            toplevel.destroy()
            return
        for panel in panels:
            panel.assign(component)
            
class DefaultMenu(Menu):
    DEFAULT_ITEMS = [
                     ['PyLAF', ],
                     ['File', FileMenu],
                     ['Edit'],
                     ['Children', ChildrenMenu],
                     ]
    ITEMS = []
    #RESTS = [
    #         ['Window', ],
    #         ['Help', ],
    #         ]
    # TODO:GUI毎に管理しなければならないパラメータの取り扱い。Componentからは初期値のみ管理。
    def __init__(self,master=None,desc=[],cnf={},**kw):
        cls = self.__class__
        #ITEMS = cls.ITEMS
        #cls.ITEMS = []
        Menu.__init__(self,master,cnf,**kw)
        self.make(cls.DEFAULT_ITEMS)
        self.make(cls.ITEMS)
        self.make_rest(self.children)
        self.remove_empty_items(self)
    def make_rest(self,children): # メニューの末尾にアイテムを追加する
        #self.make(self.__class__.RESTS)
        for key in children:
            child = children[key]
            if utils.isfamily(child,Menu):
                try: make_rest = getattr(child,'make_rest')
                except AttributeError: continue
                make_rest()
                self.make_rest(child.children)

class BaseConsole:
    # panels   = panels
    # panel    = panel
    # consoles = consoles
    console  = console
    def assign(self,component):
        self.comp = weakref.ref(component)
        self.layout().assign(component)
        self.menu().assign(component)
    def component(self,path=None):
        try: self.comp
        except AttributeError: return
        if not path: return self.comp()
        ids = path.split('.')
        child = self.comp()
        for id in ids:
            child = child.children[id]
        return child
    def menu(self):
        return self.children['menu']
    def layout(self):
        return self.children['layout']
    def panel(self,id):
        return self.layout().panel(id)
        
class Console(Tkinter.Frame,BaseConsole):
    def __init__(self,master=None,component=None,layout=Standard,sync=True,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        self.sync = sync
        # componentがClassTypeならば雛形生成モードにする
        if type(component) == types.ClassType:
            klass = component
            component = None
        else:
            klass = component.__class__
        # レイアウトを生成する
        #self.layout = weakref.ref(layout(self,klass=klass,name='layout'))
        layout(self,klass=klass,name='layout')
        # メニューを生成する
        try: menu = klass.Menu
        except AttributeError:
            #self.menu = weakref.ref(DefaultMenu(master=self,name='menu'))
            menu = DefaultMenu
            #self.menu = weakref.ref(klass.Menu(master=self,name='menu'))
        self.master.config(menu=menu(master=self,name='menu'))
        #self.master.config(menu=self.menu())
        # componentをアサインする
        if not component == None:
            self.assign(component)
        self.layout().pack(expand=True,fill=Tkinter.BOTH)
        self.pack(expand=True,fill=Tkinter.BOTH)
        if sync:
            self.polling()
    def polling(self):
        try: self.comp # すでにassignされていて
        except AttributeError: pass
        else:
            if self.component() == None: # componentが死んでいたら
                self.destroy() # 自爆して
                return # ループを抜ける
        self.after(500,self.polling)
    def destroy(self):
        if self.sync and (not self.component() == None):
            self.component().destroy()
        Tkinter.Frame.destroy(self)
        
class Embed(Tkinter.LabelFrame,BaseConsole):
    def __init__(self,master=None,klass=None,layout=PlotLayout,text=None,cnf={},**kw):
        Tkinter.LabelFrame.__init__(self,master,cnf,**kw)
        self.sync = False
        if text == None: text = self._name
        self.configure(text=text)
        self.klass = klass
        #self.layout = weakref.ref(layout(self,klass=klass))
        layout(self,klass=klass,name='layout')
        self.layout().pack(expand=True,fill=Tkinter.BOTH)
        self.make_menu(klass)
    def make_menu(self,cls):
        try: cls.Menu
        except AttributeError:
            klass = DefaultMenu
        else:
            klass = cls.Menu
        menu = klass(master=self,name='menu')
        # PyLAFメニューの削除
        index = menu.labeltoindex('PyLAF')
        if not index == None:
            menu.delete(index)
        # ポップアップイベントのバインド
        self.bind('<Control-Button-1>', self._rclicked) # Ctrl+右クリック
        if platform.system() == 'Darwin': # Darwinでは右クリックが異なる
            self.bind('<Button-2>', self._rclicked) # DarwinだったらB2
        else:
            self.bind('<Button-3>', self._rclicked) # Windows,LinuxだったらB3
    def _rclicked(self,e):
        self.menu().tk_popup(e.x_root,e.y_root)
    def destroy(self):
        if self.sync and (not self.component() == None):
            self.component().destroy()
        Tkinter.LabelFrame.destroy(self)
    def sync_on(self):
        self.sync = True
        
if __name__ == '__main__':
    import core
    from kitchen import Kitchen # gui内部からkitchenは機能しない
    '''
    テストコード
    '''
    tk = Tkinter.Tk()
    # テストコンポーネント
    class Test(core.Component):
        def __init__(self,master=None,name=None):
            core.Component.__init__(self,master,name)
            self.parametera = core.Port(0.)
            self.parameterb = core.Port(10.)
            self.parameterc = core.Port(100.)
            embed = EmbedTest(self,name='sigout')
            embed.sigin.set('updated')
        class Plot(Panel):
            def __init__(self,master=None,cnf={},**kw):
                Panel.__init__(self,master,cnf,**kw)
                Embed(self,klass=EmbedTest,layout=PlotLayout,name='sigout').grid(row=0,column=0,sticky=Tkinter.E+Tkinter.W+Tkinter.N+Tkinter.S)
                self.grid_rowconfigure(0,weight=1)
                self.grid_columnconfigure(0,weight=1)
        class Control(Panel):
            def __init__(self,master=None,cnf={},**kw):
                Panel.__init__(self,master,cnf,**kw)
                b, l, e = TableBuilder(self), Tkinter.Label, widgets.Entry
                b.add(l,text='Parameter A').grid().add(e,name='parametera').grid()
                b.add(l,text='Parameter B').grid().add(e,name='parameterb').grid()
                b.add(e,name='parameterc').grid(columnspan=2)
                b.add(l,text='Parameter D').grid().add(e,name='parameterd').grid()
                b.add(e,name='parametere').grid(columnspan=2)
                #
                self.linkmap = {
                #                'parametera'       : None,
                #                'parameterb'       : None,
                #                'parameterb.value' : 'parametera',
                                'parameterb'       : 'parametera',
                                }
                #
                e(self.widget('parametere'),name='parameterea')
                e(self.widget('parametere.parameterea'),name='parametereaa')
                #
                b = Panel(self,name='panelb')
                c = Panel(b,name='panelc')
                d = Tkinter.Frame(self)
                e = Panel(d,name='panele')
                f = Panel(d,name='panelf')
                g = Tkinter.Frame(f)
                h = Panel(g,name='panelh')
        class Config:
            class Decolation(Panel):
                def __init__(self,master=None,cnf={},**kw):
                    Panel.__init__(self,master,cnf,**kw)
                    builder = TableBuilder(self)
                    builder.add(Tkinter.Label,text='Parameter A').grid()
                    builder.add(widgets.Entry,name='parametera').grid()
                    builder.add(Tkinter.Label,text='Parameter B').grid()
                    builder.add(widgets.Entry,name='parameterb').grid()
                    builder.add(widgets.Entry,name='parameterc').grid(columnspan=2)
                    builder.add(Tkinter.Label,text='Parameter D').grid()
                    builder.add(widgets.Entry,name='parameterd').grid()
                    self.port('parameterd').bind(self._parameterd)
                    self.linkmap = {}
                def _parameterd(self):
                    value = self.port('parameterd').get()
                    self.sibling('control').port('parameterd').set(value)
    class EmbedTest(core.Component):
        def __init__(self,master=None,name=None):
            core.Component.__init__(self,master,name)
            self.a     = core.Port('a')
            self.b     = core.Port('b')
            self.c     = core.Port('c')
            self.sigin = core.Port('sigin')
        class Plot(Panel):
            def __init__(self,master=None,cnf={},**kw):
                Panel.__init__(self,master,cnf,**kw)
                builder = TableBuilder(self)
                builder.add(Tkinter.Label,text='Parameter A').grid()
                builder.add(widgets.Entry,name='a').grid()
                builder.add(Tkinter.Label,text='Parameter B').grid()
                builder.add(widgets.Entry,name='b').grid()
                builder.add(widgets.Entry,name='c').grid(columnspan=2)
                builder.add(widgets.Entry,name='sigin').grid(columnspan=2)
        class Control(Panel):
            def __init__(self,master=None,cnf={},**kw):
                Panel.__init__(self,master,cnf,**kw)
                builder = TableBuilder(self)
                builder.add(Tkinter.Label,text='Parameter A').grid()
                builder.add(widgets.Entry,name='a').grid()
                builder.add(Tkinter.Label,text='Parameter B').grid()
                builder.add(widgets.Entry,name='b').grid()
    #
    console = Console(tk,Test())
    console.master.title('console')
    #
    Tkinter.mainloop()
    # TODO: setattr(component,uuidname,port)で新しいポートを作って、リンクした後にdel uuidnameすればいい