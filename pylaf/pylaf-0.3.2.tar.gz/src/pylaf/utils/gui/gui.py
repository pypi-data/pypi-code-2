# coding: utf-8

import weakref, types

def popcnf(key,cnf):
    item = None
    if cnf.has_key(key):
        item = cnf[key]
        del cnf[key]
    return item

def convweak(method): # インスタンスメソッドを弱参照フォーマットに変換する関数
    class Dummy: pass # スコープを抜けたらすぐに解放されるダミーオブジェクト用のクラス
    result = (weakref.ref(Dummy()),'') # 空の参照
    if method == None: return result # もしメソッドが未定義ならば空の参照を返す
    if type(method) == tuple: # それがすでに弱参照フォーマットならば
        result = method # そのまま返す。
    if type(method) == types.MethodType: # それがメソッドならば
        result = (weakref.ref(method.__self__),method.__name__) # 弱参照フォーマットに変換する。
    return result

def kw(**kw): return kw

class SyncVarPort:
    def _backward(self,*args):
        try: self._backward_called
        except AttributeError:
            self._backward_called = True
            self.value.set(self.var.get())
            del self._backward_called
    def _forward(self):
        try: self._forward_called
        except AttributeError:
            self._forward_called = True
            self.var.set(self.value.get())
            del self._forward_called

class WithGUI:
    '''
    GUIとの寿命同期機構など、GUIとの連携に必要な機構を格納する。
    def destroy(self):
        if self._dying: return
        self._dying = True
        WithGUI.destroy(self)
        core.Component.destroy(self)
    '''
    def __init__(self):
        self._guis = weakref.WeakValueDictionary()
        self._dying = False
    def destroy(self):
        for key in self._guis:
            gui = self._guis[key]
            if gui._sync: gui.destroy()
