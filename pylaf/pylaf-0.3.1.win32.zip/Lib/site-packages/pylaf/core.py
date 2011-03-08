# coding: utf-8

import utils.core, weakref, inspect

def kw(**kwargs): return kwargs
def args(*args,**kwargs): return (args,kwargs)

def get_child(ins,id):
    id = id.split('.')
    obj = ins
    for name in id: obj = obj.children[name]
    return obj
    
def get_port(ins,id):
    idl = id.split('.')
    id, name = idl[0], idl[-1]
    for o in idl[1:-1]: id = id + '.' + o
    return getattr(get_child(ins,id),name)
    
EVENT_SET, EVENT_GET = range(2)
    
class CallWrapper:
    def __init__(self,method):
        self.weakref_obj = None
        self.method_name = None
        self.function    = None
        try: method.__self__ # もしも関数や部分引数オブジェクトだったら
        except AttributeError: # もし関数だったら
            self.function = method
        else: # それ以外だったら
            # obj: インスタンス, name: メソッド名
            obj, name = method.__self__, method.__name__
            self.weakref_obj = weakref.ref(obj)
            self.method_name = name
    def ismethod(self):
        return (not self.weakref_obj == None) and (self.function == None)
    def isfunction(self):
        return (self.weakref_obj == None) and (not self.function == None)
    def isalive(self):
        if   self.ismethod():
            # 参照可能か？インスタンスが生きているか？
            try: o = self.weakref_obj()
            except TypeError: return False
            # メソッドにアクセス可能か？
            try: getattr(o,self.method_name)
            except AttributeError: return False
        elif self.isfunction():
            return True
        else: return False
        return True
    def __call__(self,*args,**kwargs):
        if self.isalive():
            if   self.ismethod():
                o, name = self.weakref_obj(), self.method_name
                return getattr(o,name).__call__(*args,**kwargs)
            elif self.isfunction():
                return self.function(*args,**kwargs)
    def __eq__(self,other):
        try: o, q = self.weakref_obj(), other.weakref_obj()
        except TypeError: return False
        return (o == q) and (self.method_name == other.method_name) and (self.function == other.function)
    
class Root:
    __metaclass__ = utils.core.Singleton
    def __init__(self):
        self.children = {}
    def destroy(self):
        for c in self.children.values(): c.destroy()

class Port(utils.core.Observer):
    def __init__(self,*args,**kw):
        if utils.isfamily(args[0],Port): # 引数がポート一族であれば
            s = Storage(args[0].get()) # ポートのデータを初期値として新規サブジェクトを生成し
            utils.core.Observer.__init__(self,s) # サブジェクトを監視するオブザーバを生成する
        else: # 引数がその他であれば
            s = Storage(*args,**kw) # 引数を初期値としてサブジェクトを生成し
            utils.core.Observer.__init__(self,s) # サブジェクトを監視するオブザーバを生成する
        self._callbacks = [] # コールバックを保持するタプル(obj,name)を生成する。
        self._iscaller = False
    def update(self,event,*args): # 監視しているストレージが更新したら直接起動されるメソッド。
        if event == EVENT_GET: return # もしGETイベントならばなにもしない
        callbacks = list(self._callbacks)
        for callback in callbacks:
            if not callback.isalive(): self._callbacks.remove(callback)
            callback.__call__()
    def bind(self,method): # 監視しているストレージが更新したら起動したいメソッドを登録する。
        self._callbacks.append(CallWrapper(method))
        return self
    def unbind(self,method):
        self._callbacks.remove(CallWrapper(method))
    def unbind_all(self):
        callbacks = list(self._callbacks)
        for callback in callbacks: self._callbacks.remove(callback)
    def passive(self):
        self._deposit = self._callbacks
        self._callbacks = []
    def active(self):
        try: self._deposit
        except AttributeError: return
        for callback in self._callbacks: self._deposit.append(callback)
        self._callbacks = self._deposit
        del self._deposit
    def isoutput(self,klass):
        family = inspect.getmro(klass)
        for c in family:
            name = repr(c).split()[1]
            if name == 'PyLAF.core.Output' or name == 'core.Output':
                return True
        return False
    def link(self,*ports,**kw):
        # 空の弱参照をクリーンアップ
        for port in ports: # リンク対象のポートについてそれぞれ
            port.subject.observers.cleanup() # ポートが参照しているストレージの監視リストのdead参照を掃除し
        # リンクするアウトプット数を調べる
        outputs = []
        for obj in self.subject.observers.tolist():
            if self.isoutput(obj.__class__):
                outputs.append(obj)
        for port in ports: # リンク対象のポートについてそれぞれ
            for obj in port.subject.observers.tolist(): # ストレージを監視するポートすべてについて
                if self.isoutput(obj.__class__):
                    outputs.append(obj)
        if len(outputs) > 1:
            raise ValueError('too many Output was linked')
        # セットオプションの読み出し
        def _kw(set=False): return set
        set = _kw(**kw)
        for port in ports: # リンク対象のポートについてそれぞれ
            if set: port.set(self.get())
            for obj in port.subject.observers.tolist(): # ストレージを監視するポートすべてについて
                obj.register(self.subject) # 自身の監視するポートを監視させる
        return self
    def unlink(self):
        self.unregister()
        self.register(Storage(None))
    def set(self,*args,**kw):
        # Tk.widgetとの同期などの際に、循環呼び出しが発生しないように
        try: self._set_called # 呼び出し元フラグが存在しなければ
        except AttributeError:
            self._set_called = True # 呼び出し元フラグを生成し
            self.subject.set(*args,**kw) # ストレージに値を設定しコールバックを呼び出し
            del self._set_called # 呼び出し元フラグを削除する
    def get(self):
        return self.subject.get()

class Output(Port): # PULL型のポート
    def update(self,event,*args): # 監視しているストレージが更新したら直接起動されるメソッド。
        if event == EVENT_SET: return # もしSETイベントならばなにもしない
        callbacks = list(self._callbacks)
        for callback in callbacks:
            if not callback.isalive(): self._callbacks.remove(callback)
            callback.__call__()

class Storage(utils.core.Subject):
    '''
    複数のPortクラスで同期する任意のリテラルを格納する実体クラス
    メンバ変数による参照禁止
    '''
    def __init__(self,*args,**kw): # 与えられた値を保持するストレージを生成する
        utils.core.Subject.__init__(self)
        self._set(*args,**kw)
    def _set(self,*args,**kw):
        #    self.value = value.copy() # もしvalueがcopyメソッドを持っていればvalue.copy()する
        #    # ！！！listはcopyメソッドを持たないから、Portの実装に影響するかも！！！
        if args and kw:
            args = tuple([utils.core.itemcopy(item) for item in args]) # タプルの中身をコピーする（１階層のみ）
            temp = {}
            for key in kw:
                temp[key] = utils.core.itemcopy(kw[key])
            kw = temp
            self.value = (args,kw)
        elif args:
            if len(args) == 1:
                self.value = utils.core.itemcopy(args[0])
            else:
                self.value = tuple([utils.core.itemcopy(item) for item in args]) # タプルの中身をコピーする（１階層のみ）
        elif kw:
            temp = {}
            for key in kw: temp[key] = utils.core.itemcopy(kw[key])
            self.value = temp
    def set(self,*args,**kw):
        self._set(*args,**kw)
        self.notify(EVENT_SET)
    def get(self):
        '''格納しているオブジェクトまたはリテラルを返す'''
        self.notify(EVENT_GET)
        return self.value

class Component:
    '''
    PyLAF.Rootを基盤とするPyLAFコンポーネント
    メンバ変数による参照禁止
    '''
    def __init__(self,master=None,name=None):
        self.children = {}
        if master == None: self.master = Root()
        else: self.master = master
        if name == None: self._name = repr(id(self))
        else: self._name = name
        self._assign_to_master()
    def _assign_to_master(self):
        if self.master.children.has_key(self._name): # master.childrenにおけるidの唯一性を保証する
            self.master.children[self._name].destroy()
        self.master.children[self._name] = self
    def _remove_from_master(self): # master.childrenから自身へのオブジェクト参照を廃棄する
        if self.master.children.has_key(self._name):
            del self.master.children[self._name]
    def destroy(self):
        ''' Destroy this and all descendants nodes.'''
        for c in self.children.values(): c.destroy() # 子オブジェクトを巡回してdestroy()をコールする
        self._remove_from_master() # 親オブジェクトのchildren辞書から自身の参照を削除する
        # ^^^ 辞書の巡回中に辞書を変更しちゃって大丈夫？
        # self.children.clear() で一気に削除するほうが行儀いいのでは？

# class Trig:
if __name__ == "__main__":
    class Child(Component): pass
    class MyComponent(Component):
        def __init__(self,master):
            Component.__init__(self,master)
            self.port = Port(0).bind(self.callback) # Portが自身のメソッドへアクセスできかつきちんとselfが解放される
            # 子ノードがぶら下げられても、メンバ変数として保持しなければselfが解放されるが
            c = Child(self,name='child'); print c
            # === メンバ変数として保持するとselfが解放されなくなる
            # self.child = Child(self,name='child'); print self.child
            # ===
        def callback(self):
            print self.port.get(), self.children['child']
        # destroyでPortやComponentのメンバ変数を解放するのは賢いか？シンプルではない。
        # Portがメソッドを弱参照するように、master.childrenを弱参照で保持するようにすれば自動的に解放されるようになる
    c = MyComponent(Root())
    print c.port.get()
    c.port.set('aa',xaxis='aa')
    c.port.set(xaxis='aa')
    c.port.set('%d aa' % 1)
    c.port.unbind(c.callback) # バインドの解除
    # c.port.unbind_all() # バインドの解除
    c.port.set('aa',xaxis='aa')
    
    c = weakref.ref(c)
    print c
    c().destroy()
    print c
    