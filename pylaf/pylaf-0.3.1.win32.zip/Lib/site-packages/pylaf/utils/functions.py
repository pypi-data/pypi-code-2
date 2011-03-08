# coding: utf-8

import inspect, weakref

def isfamily(obj,cls): # インスタンスobjがクラスclsの一族であるかどうか調べる
    try:
        bases = inspect.getmro(obj.__class__) # オブジェクトのクラスツリーをリストで返す
    except AttributeError: # クラスでなければ？偽を返す
        return False
    if bases.count(cls): # クラスツリーにclsが含まれるならば
        return True
    else:
        return False

def args(*args,**kw): return args,kw

def parse_port_args(arg):
    if not type(arg) == tuple: return (arg,),{}
    if not len(arg) == 2: return arg,{}
    if not (type(arg[0]) == tuple and type(arg[1]) == dict): return arg,{}
    return args(*arg[0],**arg[1])

def test_parse():
    print parse_port_args('item')
    print parse_port_args(('item','item2','item3'))
    print parse_port_args((('item','item2','item3'),{'key1':'item1'}))

def caller():
    '''
    下記ブログに掲載されていたコードを使わせてもらった
    http://d.hatena.ne.jp/Kazumi007/20090914/1252915940
    !!!EzPortの中で使ったらコンポーネントが解放されなくなったので、要注意!!!
    '''
    try:
        framerecords = inspect.stack()
        framerecord  = framerecords[2]
        frame        = framerecord[0]
        arginfo      = inspect.getargvalues(frame)
        return arginfo.locals['self'] if 'self' in arginfo.locals else None
    finally:
        del frame
    return None

class Dummy(): pass
Wnone = weakref.ref(Dummy())
