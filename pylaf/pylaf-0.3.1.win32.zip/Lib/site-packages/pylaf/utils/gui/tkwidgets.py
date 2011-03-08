# coding: utf-8

import Tkinter
from gui import convweak

class NamePlate(Tkinter.Frame):
    def __init__(self,master=None,name='',cnf={},**kw):
        Tkinter.Frame.__init__(self,master,cnf,**kw)
        Tkinter.Label(self,text=name).pack(side=Tkinter.TOP,expand=1,fill=Tkinter.X)

class WeakValuedButton(Tkinter.Button):
    '''クリックすると登録したコールバックを起動する。コールバックは通常のTkinter.Buttonと同様にcommand=<method>オプションで指定できる。'''
    def __init__(self,master=None,cnf={},**kw):
        Tkinter.Button.__init__(self,master,cnf,**kw)
        self.configure(command=self._clicked) # ボタンへのコールバックを設定する
    def _configure(self,cmd,cnf,kw):
        command = None
        if cnf:
            if cnf.has_key('command'):
                command = cnf['command']
                cnf['command'] = self._clicked
        if kw: # もしkwが存在して
            if kw.has_key('command'): # 'command'キーを持っていれば
                command = kw['command'] # コマンドの内容を控え
                kw['command'] = self._clicked # 弱参照呼び出しコールバックにすり替える
        if command: # commandが設定されていれば
            self._callback = convweak(command) # callbackにメソッドの弱参照を設定し
        Tkinter.Button._configure(self,cmd,cnf,kw) # 設定コマンドを呼び出す
    def _clicked(self):
        try: self._callback # もしコールバックが定義されていて
        except AttributeError: pass
        else:
            if not self._callback[0]() == None: # 参照先が削除されていなければ
                wobj, method = self._callback
                getattr(wobj(),method).__call__() # メソッドをコールする
            else:
                del self._callback # 参照先が存在していなければコールバックを削除する
