# coding: utf-8

import weakref

# listと完全互換で内部処理だけweakrefってのが理想なんだけど．．．結構大変そう

class WeakValueList(list):
    '''
    オブジェクトの弱参照を保持するリスト
    '''
    def count(self,x):
        return list.count(self, weakref.ref(x))
    def append(self,obj):
        '''objへの弱参照をリストへ追加する'''
        list.append(self, weakref.ref(obj))
    def insert(self,index,obj):
        '''objへの弱参照をindex番目に挿入する'''
        list.insert(self, index, weakref.ref(obj))
    def remove(self,obj):
        '''objへの弱参照のうち最初のひとつをリストから削除する'''
        '''もしobjが見つからなければエラーを返す'''
        for ref in self: # 弱参照をひとつづつ取り出し
            if obj is ref(): # もし、弱参照がobjへのものならば
                list.remove(self, ref) # リストからobjへの弱参照を削除し
                return # ループから抜け出す
        raise ValueError
    def tolist(self):
        '''弱参照のリストを参照のリストへ変換する'''
        return [ref() for ref in self]
    def cleanup(self):
        '''
        dead参照のアイテムを削除する
        '''
        items = [] # リストを正しく巡回するために良いしたdead参照を保持するためのバッファ
        for ref in self: # リストを巡回し
            if ref() == None: # dead参照を見つけたら
                items.append(ref) # バッファにためる
        for item in items: # バッファを巡回し
            list.remove(self, item) # dead参照を削除する
    
if __name__ == '__main__':
    '''Test Code'''
    '''含まれていない要素の場合、raiseされるかremoveをテストする'''
    class Dummy: pass
    abc, defg, hijkl = Dummy(), Dummy(), Dummy()
    print abc, defg, hijkl
    l = WeakValueList()
    l.append(abc); l.append(defg); l.append(hijkl)
    print l.count(defg)
    l[0] = abc
    print l, l[0]
    for c in l:
        print c
