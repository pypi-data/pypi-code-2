# coding: utf-8

import weakvaluelist

class Observer:
    '''Subjectの監視者。単一のSubjectを監視する。メンバ変数による参照禁止'''
    def __init__(self,subject):
        self.subject = None # 監視対象を保持するための参照
        self.register(subject) # 監視対象の登録
    def register(self,subject):
        self.unregister() # 監視を解除
        subject.register(self) # 監視していることを通知
        self.subject = subject # 監視対象を保持するために参照する
    def unregister(self):
        if not self.subject == None: # すでになにかを監視しているならば
            self.subject.unregister(self) # 監視をやめることを通知
            self.subject = None # 監視対象保持のための参照を削除
    def update(self,*args,**kw): pass # 監視対象が変化したときに起動される抽象メソッド

class Subject:
    '''監視対象。いずれからも監視されなくなったら自動的に削除される。メンバ変数による参照禁止'''
    def __init__(self):
        self.observers = weakvaluelist.WeakValueList() # オブザーバとの循環参照を防ぐため弱参照のリストを格納に使う
    def register(self,observer):
        if not self.observers.count(observer): # もし、observerの弱参照を保持していなければ
            self.observers.append(observer) # オブザーバの弱参照をリストに保持
    def unregister(self,observer):
        self.observers.cleanup() # 削除したオブジェクトをコールしないよう空になった弱参照をクリア
        self.observers.remove(observer) # 与えられたオブザーバの弱参照をリストから削除
    def notify(self,*args,**kw):
        '''監視者へ変更を通知する。Observer.update()を起動する。起動の順番は登録順。'''
        self.observers.cleanup() # 削除したオブジェクトをコールしないよう空になった弱参照をクリア
        for o in self.observers.tolist(): o.update(*args,**kw) # オブザーバひとつひとつのupdate()をobserversの順番に起動

import weakref
if __name__ == '__main__':
    '''Test Code'''
    ''' いずれからも監視されなくなったらSubjectが解放されることを確認する'''
    s1 = Subject() # Subjectを生成する
    o1a = Observer(s1) # s1の監視者を生成
    o1b = Observer(s1) # s1の監視者を生成
    ws1 = weakref.ref(s1); s1  = None # Subjectへの参照s1を削除する
    print ws1() # このとき、o1a, o1bからの監視によりSubjectは保持されている
    o1a, o1b = None, None # Observerへの参照o1a, o1bを削除する
    print ws1() # いずれからも監視されなくなったSubjectは解放されている
