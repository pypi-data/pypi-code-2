# coding: utf-8

import Tkinter
import ttk #@UnresolvedImport
import core, gui, mpl, uuid, inspect

PRIMARY_PORTS = {gui.Button:          'value',
                 gui.Entry:           'value',
                 gui.Label:           'value',
                 gui.EntryTable:      'value',
                 gui.LabelTable:      'value',
                 gui.MultipleEntries: 'value',
                 mpl.BasePlot:        'sigin'}

class FactoryPort:
    SEQUENCE = None
    ITEMS    = None
    @classmethod
    def reset(cls):
        cls.SEQUENCE = None
        cls.ITEMS    = None
    def __init__(self):
        self.reset()
    def gui(self,widget_klass,cnf={},*args,**kw):
        # 
        if FactoryPort.SEQUENCE == None:
            FactoryPort.SEQUENCE = []
            FactoryPort.ITEMS    = {}
        # オプションのマージ
        for key in cnf:
            kw[key] = cnf[key]
        #
        FactoryPort.SEQUENCE.append(self)
        FactoryPort.ITEMS[self] = {'widget_klass': widget_klass}
        #
        def option(master=None,name=None,**kw): return kw # master,nameは無効
        kw = option(**kw)
        if not kw:
            kw = {}
        FactoryPort.ITEMS[self]['widget_args']   = args
        FactoryPort.ITEMS[self]['widget_kwargs'] = kw
        return self
    def map(self,**kw):
        FactoryPort.ITEMS[self]['map'] = kw
        return self
    def grid(self,**kw):
        def option(row=0,column=0,rowspan=0,columnspan=0,**kw): return kw
        FactoryPort.ITEMS[self]['grid_option'] = option(**kw)
        return self
    def label(self,text='',label_klass=ttk.Label,**kw):
        kw['text'] = text
        FactoryPort.ITEMS[self]['label_option'] = kw
        FactoryPort.ITEMS[self]['label_klass']  = label_klass
        return self
    def label_grid(self,**kw):
        def option(row=0,column=0,rowspan=0,columnspan=0,**kw): return kw
        FactoryPort.ITEMS[self]['label_grid_option'] = option(**kw)
        return self

class Port(core.Port,FactoryPort):
    def __init__(self,*args,**kw):
        core.Port.__init__(self,*args,**kw)
        FactoryPort.__init__(self)

class Output(core.Output,FactoryPort):
    def __init__(self,*args,**kw):
        core.Output.__init__(self,*args,**kw)
        FactoryPort.__init__(self)

class Grid(gui.Grid):
    _ezcomponent = None
    _ezcounter   = 0
    @classmethod
    def make(cls,component):
        try: cls._ezlock
        except AttributeError: pass
        else:
            FactoryPort.reset()
            return
        def extract_name(port):
            members = inspect.getmembers(component)
            objs    = [obj for name,obj in members]
            if objs.count(port):
                index = objs.index(port)
                name  = members[index][0]
                return name
        def append(port):
            klass = FactoryPort.ITEMS[port]['widget_klass']
            name  = FactoryPort.ITEMS[port]['name']
            try:
                args = FactoryPort.ITEMS[port]['widget_args']
            except KeyError:
                args = ()
            try:
                kwargs = FactoryPort.ITEMS[port]['widget_kwargs']
            except KeyError:
                kwargs = {}
            option = (args,kwargs)
            #
            try:
                o = FactoryPort.ITEMS[port]['label_option']
            except KeyError:
                label = None
            else:
                try:
                    label = o['text']
                    del o['text']
                except KeyError:
                    label = None
            #
            try:
                map = FactoryPort.ITEMS[port]['map']
            except KeyError:
                map = {}
            if PRIMARY_PORTS.has_key(klass):
                if not map.has_key(PRIMARY_PORTS[klass]):
                    map[PRIMARY_PORTS[klass]] = name
            #
            try:
                geometry = FactoryPort.ITEMS[port]['grid_option']
            except KeyError:
                geometry = {}
            try:
                label_widget = FactoryPort.ITEMS[port]['label_option']
            except KeyError:
                label_widget = {}
            try:
                label_geometry = FactoryPort.ITEMS[port]['label_grid_option']
            except KeyError:
                label_geometry = {}
            cls._ezconfig.append((klass,
                                  name,
                                  option,
                                  label,
                                  map,
                                  geometry,
                                  label_widget,
                                  label_geometry))
        #
        cls._ezconfig = []
        # アトリビュート名とポートオブジェクトの対応マップを生成する
        for port in FactoryPort.SEQUENCE:
            name = extract_name(port)
            if name:
                FactoryPort.ITEMS[port]['name'] = name
        # アイテムを登録する
        for port in FactoryPort.SEQUENCE:
            append(port)
        FactoryPort.reset()
        # ファクトリの受付終了
        cls._ezlock    = True
        cls._ezcounter = 0
    @classmethod
    def _initialize(cls):
        # いちばん最初の呼び出しの際に生成ルールリストを用意する
        try: cls._ezconfig
        except AttributeError: cls._ezconfig = []
        try: cls._primary
        except AttributeError:
            cls._primary = {gui.Button:          'value',
                            gui.Entry:           'value',
                            gui.Label:           'value',
                            gui.EntryTable:      'value',
                            gui.LabelTable:      'value',
                            gui.MultipleEntries: 'value'}
    @classmethod
    def _append(cls,
                klass,
                name=None,
                label=None,
                map=None,
                geometry=None,
                label_widget=None,
                label_geometry=None,
                cnf=None,
                *args,
                **kwargs):
        # 呼び出しカウンタをインクリメントする
        cls._ezcounter += 1
        # ロックされていなければ生成ルールを追加する
        try: cls._ezlock
        except AttributeError:
            # デフォルトの辞書を生成する
            if map            == None: map            = {}
            if geometry       == None: geometry       = {}
            if label_widget   == None: label_widget   = {}
            if label_geometry == None: label_geometry = {}
            if cnf            == None: cnf            = {}
            # nameが未定義ならばuuidをnameとする
            if name == None: name = str(uuid.uuid4())
            # mapにデフォルトポートが含まれていなければ追加する
            if cls._primary.has_key(klass):
                if not map.has_key(cls._primary[klass]):
                    map[cls._primary[klass]] = name
            # ウィジェット生成オプションの処理
            for key in cnf: kwargs[key] = cnf[key] # kwargsにwidgetを上書き追加する
            for key in ('master'): # masterは無効にする
                if kwargs.has_key(key): del kwargs[key]
            option = (args,kwargs)
            # ウィジェット生成情報の登録
            cls._ezconfig.append((klass,name,option,label,map,geometry,label_widget,label_geometry)) # アイテムリストへ追加する
        # プライマリポートを返す
        klass = cls._ezconfig[cls._ezcounter - 1][0]
        map   = cls._ezconfig[cls._ezcounter - 1][4]
        if not cls._primary.has_key(klass): return None # プライマリポートがない
        if not map.has_key(cls._primary[klass]): return None # プライマリポートがない
        return map[cls._primary[klass]] # プライマリポートを返す
    @classmethod
    def _genport(cls,component,id,value,link,bind):
        '''
        ポートを自動生成してメソッドのバインドを試みる。
        componentが未定義であった場合にはなにもしない。
        メソッドをバインドする：
            bindが指定されている場合
            mapで指定されたプライマリポート名に対応するメソッドが存在する場合
        '''
        if component == None: return # コンポーネントが指定されていなければなにもしない
        setattr(component,id,core.Port(value)) # valueを初期値としてポートを生成する
        # ポートのリンク
        def plink(src,target):
            if src.get() == None: target.link(src,set=True)
            else: src.link(target)
        if not link == None:
            if type(link) == tuple:
                for o in link: plink(getattr(component,id),o)
            else:
                plink(getattr(component,id),link)
        # メソッドの自動バインド
        if bind == None:
            try: bind = getattr(component,'_%s' % id)
            except AttributeError: return # mapで指定されたプライマリポート名に対応するメソッドがなければなにもしない
        if type(bind) == tuple:
            for o in bind: getattr(component,id).bind(o)
        else:
            getattr(component,id).bind(bind)
    @classmethod
    def append(cls,
               klass, # ウィジェットクラス
               name=None, # ウィジェットのアクセスid
               label=None, # グリッドラベル文字列
               map=None, # ポートの結合マップ
               component=None, # ポートの制御オプション
               value=None, # ポートの制御オプション
               link=None, # ポートの制御オプション
               bind=None, # ポートの制御オプション
               geometry=None, # ジオメトリマネージャへのオプション
               label_widget=None, # ラベルウィジェットの生成オプション
               label_geometry=None, # ラベルのジオメトリマネージャへのオプション
               cnf=None, # ウィジェットの生成オプション
               *args, # ウィジェットの生成オプション
               **kwargs): # ウィジェットの生成オプション
        '''
        ウィジェットの生成ルールを登録する。
        プライマリポートへリンクするポート名を返す。プライマリポートが登録されていなければNoneを返す。
        ルールの登録が終了したらEz.Grid.finish()を呼ばなければならない。
        
        name:           ウィジェットのアクセスid。未定義ならばuuidが生成される。
        label:          グリッドラベル文字列
        map:            ポートのリンクルール{'guiportname':'componentportname'}
                        プライマリポートはnameへリンクするようにデフォルトで設定されるがmapの指定が優先。
        widget:         ウィジェット生成オプション。masterは無効。
        geometry,       
        label_widget,   
        label_geometry: gui.Grid.appendにバイパス
        *args,          
        **kwargs:       ウィジェット生成オプション。masterは無効。
        
        component:      ポートを生成したいコンポーネントインスタンス
                        指定するとプライマリポートとリンクするポートの自動生成、メソッドのバインドと他のポートとのリンクを試みる。
                        プライマリポートが登録されていない場合にはなにもしない。
                        生成するポートの属性名はmapで指定された値に、未指定ならばウィジェットのアクセスidになる。
        value:          生成するポートの初期値
        bind:           ポートに結合するメソッド（methodまたは(method1,method2,...)）
                        bindで指定したメソッドを自動生成したポートとただちにバインドする。
                        bindで定義したメソッドが存在しない場合にはエラーを返す。
                        bindが未定義ならば'_プライマリポート名'のメソッドとのバインドを試みる。
                        このとき、メソッドが存在しない場合にはなにもしない。
        link:           ポートにリンクするポート(portまたは(port1,port2,...))
                        linkで指定したポートを自動生成したポートとただちにリンクする。
                        linkで指定したポートが存在しない場合にはエラーを返す。
        
        self.Component.append(Entry,name='entry',label='entry',component=self,value=0.)
        self.Component.append(Entry,name='entry',label='entry')
        self.entry = Port(0.).bind(self._entry)
        
        self.Component.append(Widget,label='widget',map=kw(value='win',remote='wremote'),component=self)
        self.Component.append(Widget,label='widget',map=kw(value='win',remote='wremote'))
        self.win = Port(None).bind(self._win)
        '''
        cls._initialize()
        id = cls._append(klass,name,label,map,geometry,label_widget,label_geometry,cnf,*args,**kwargs)
        if not id == None: cls._genport(component,id,value,link,bind)
        return id
    @classmethod
    def finish(cls):
        cls._ezlock    = True
        cls._ezcounter = 0
    @classmethod
    def primary(cls,klass,name):
        cls._initialize()
        cls._primary[klass] = name
    def __init__(self,master=None,cnf={},**kw):
        gui.Grid.__init__(self,master,cnf,**kw)
        for klass,name,option,label,map,geometry,label_widget,label_geometry in self._ezconfig:
            args,kwargs = option
            # kwargs中のcommandを処理する（ボタンの関数割り当てなど）
            gui.Grid.append(self,klass(master=self,name=name,*args,**kwargs),label=label,geometry=geometry,label_widget=label_widget,label_geometry=label_geometry)
    def assign(self,component):
        '''
        mapのkeyをgui側、itemをcomponent側としてポートをリンクする
        '''
        for klass,name,option,label,map,geometry,label_widget,label_geometry in self._ezconfig:
            widget = self.children[name]
            for key in map:
                gui,cmp = key,map[key]
                gui,cmp = getattr(widget,gui), getattr(component,cmp)
                # もしコンポーネント側のポート値がNoneであればWidget側のデータを用いる
                if cmp.get() == None:
                    gui.link(cmp)
                else:
                    cmp.link(gui,set=True)

class Plot(Tkinter.Frame): # Grid互換
    _ezcomponent = None
    _ezcounter   = 0
    _primary = {mpl.BasePlot: 'sigin'}
    @classmethod
    def make(cls,component):
        try: cls._ezlock
        except AttributeError: pass
        else:
            FactoryPort.reset()
            return
        def extract_name(port):
            members = inspect.getmembers(component)
            objs    = [obj for name,obj in members]
            if objs.count(port):
                index = objs.index(port)
                name  = members[index][0]
                return name
        def append(port):
            klass = FactoryPort.ITEMS[port]['widget_klass']
            name  = FactoryPort.ITEMS[port]['name']
            try:
                kwargs = FactoryPort.ITEMS[port]['widget_kwargs']
            except KeyError:
                kwargs = {}
            #
            try:
                map = FactoryPort.ITEMS[port]['map']
            except KeyError:
                map = {}
            if PRIMARY_PORTS.has_key(klass):
                if not map.has_key(PRIMARY_PORTS[klass]):
                    map[PRIMARY_PORTS[klass]] = name
            #
            cls._ezconfig.append((klass,name,map,kwargs))
        #
        cls._ezconfig = []
        # アトリビュート名とポートオブジェクトの対応マップを生成する
        for port in FactoryPort.SEQUENCE:
            name = extract_name(port)
            if name:
                FactoryPort.ITEMS[port]['name'] = name
        # アイテムを登録する
        for port in FactoryPort.SEQUENCE:
            append(port)
        FactoryPort.reset()
        # ファクトリの受付終了
        cls._ezlock    = True
        cls._ezcounter = 0
    @classmethod
    def append(cls,klass,name=None,map=None,**kw):
        # いちばん最初の呼び出しの際に生成ルールリストを用意する
        try: cls._ezconfig
        except AttributeError: cls._ezconfig = []
        #
        # 呼び出しカウンタをインクリメントする
        cls._ezcounter += 1
        # ロックされていなければ生成ルールを追加する
        try: cls._ezlock
        except AttributeError:
            cls._ezconfig.append((klass,name,map,kw))
    @classmethod
    def finish(cls):
        cls._ezlock    = True
        cls._ezcounter = 0
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        for klass,name,map,kw in self._ezconfig:
            gui.Layout.Embed(self,klass,name=name,text=name).pack(side=Tkinter.LEFT)
    def assign(self,component):
        def text(frametext=None,**kw): return frametext
        def option(frametext=None,**kw): return kw
        for klass,name,map,kw in self._ezconfig:
            self.children[name].assign(klass(component)) # 生存関係を親コンポーネントに同期した無名のコンポーネントを生成する
            # フレームラベルオプションの処理
            s = text(**kw)
            if s: self.children[name].configure(text=s)
            # プロッタのオプションを設定する
            for key in option(**kw):
                o = getattr(self.children[name].children['plot'],key)
                o.set(kw[key])
            # ポート間を結合する。
            if map == None: map = {} # ポートマップが未定義なら空辞書を用意
            if self._primary.has_key(klass): # プライマリーポートが既知ならば
                primary = self._primary[klass] # プライマリポート名を取得して
                if not map.has_key(primary): # mapにプライマリポートが含まれていなければ
                    map[primary] = name # nameで指定されるポートとプライマリポートをマッピングする
            for key in map:
                dest = getattr(self.children[name].comp(),key)
                dept = getattr(component,map[key])
                dest.set(dept.get()); dept.link(dest)
            
if __name__ == '__main__':
    class BasicSample(gui.ComponentWithGUI): # フレームワークの基本機能を使ったGUIの構築例
        class Console(Grid): pass # __metaclass__ = Meta
        def __init__(self,master=None,name=None):
            gui.ComponentWithGUI.__init__(self,master,name)
            # 
            self.Console.append(gui.Entry,label='entry',name='entryq')
            self.entryq = core.Port(0.).bind(self._entry)
            # ポートの自動生成、メソッドの自動割り当て（標準記法）
            self.Console.append(gui.Entry,label='entry',name='entry',component=self,value=0.)
            # ポートの自動生成、メソッドの指定割り当て
            self.Console.append(gui.Entry,label='entry',name='entry1',component=self,value=0.,bind=self._entry)
            # mapの指定
            self.Console.append(gui.Entry,label='entry',name='entrxy',map=core.kw(value='entry'))
            self.entry = core.Port(0.).bind(self._entry)
            # 標準機法(mapの省略)
            # 
            print self.Console.append(gui.Entry,name='1entry',label='entry',component=self,value=0.)
            #self.entry = core.Port(0.).bind(self._entry)
            print self.Console.append(gui.Entry,name='entry2',label='entry',component=self,value=0.)
            # idの自動生成、ポートの自動生成
            self.id = self.Console.append(gui.Entry,label='entry',component=self)
            # idの自動生成、ポートの自動生成、メソッドの指定割り当て（標準記法）
            self.Console.append(gui.Button,text=u'実行',component=self,bind=self._button)
            # idの自動生成
            id = self.Console.append(gui.Button,text=u'実行')
            setattr(self,id,core.Port(None).bind(self._button))
            class Test(core.Component):
                def __init__(self,master=None,name=None):
                    core.Component.__init__(self,master,name)
                    self.value  = core.Port(0.).bind(self._value)
                    self.value2 = core.Port(1.).bind(self._value2)
                    self.value3 = core.Port(2.).bind(self._value3)
                def _value(self): print 'value:', self.value.get()
                def _value2(self): print 'value2:', self.value2.get()
                def _value3(self): print 'value3:', self.value3.get()
            class MyEntry(gui.Entry): pass
            # bindオプションのテスト
            self.Console.append(gui.Entry,label='entry',component=self,bind=self._linktest)
            self.Console.append(gui.Entry,label='entry',component=self,bind=(self._linktest2,self._linktest3))
            # linkオプションの活用　無名ポートの活用幅を広げる
            test = Test(self,name='test')
            self.Console.append(gui.Entry,label='entry',component=self,link=test.value)
            self.Console.append(gui.Entry,label='entry',component=self,link=(test.value2,test.value3))
            self.Console.append(MyEntry,label='entry',component=self,link=test.value)
            self.Console.primary(MyEntry,'value')
            self.Console.append(MyEntry,label='entry',component=self,link=test.value)
            #
            self.Console.finish()
        def _entry(self):
            print 'entry'
        def _button(self):
            print 'button:', getattr(self,self.id).get()
        def _linktest(self):
            print 'linktest:', self.children['test'].value.get()
        def _linktest2(self):
            print 'linktest2:', self.children['test'].value2.get()
        def _linktest3(self):
            print 'linktest3:', self.children['test'].value3.get()
    BasicSample().destroy()
    
    class OtherSample(gui.ComponentWithGUI):
        class Console(Grid): pass
        def __init__(self,master=None,name=None):
            gui.ComponentWithGUI.__init__(self,master,name)
            self.Console.append(gui.Entry,label='entry',name='entry',component=self,value=0.)
            self.Console.finish()
        def _entry(self):
            print 'other_entry'
    OtherSample().destroy()
    
    import weakref,gc
    tk = Tkinter.Tk()
    basic = gui.Layout.Application(tk,BasicSample(core.Root()),title='basic sample',sync=False)
    gui.Layout.Application(Tkinter.Toplevel(tk),BasicSample(core.Root()))
    gui.Layout.Application(Tkinter.Toplevel(tk),BasicSample)
    gui.Layout.Application(Tkinter.Toplevel(tk),OtherSample(core.Root()))
    Tkinter.mainloop()
    basic = weakref.ref(basic)
    gc.collect()
    print 'basic:', basic
