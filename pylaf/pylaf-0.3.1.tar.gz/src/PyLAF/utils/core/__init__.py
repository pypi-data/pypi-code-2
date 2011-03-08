# coding: utf-8
'''
PyLAF.coreを動作させるのに最低限必要なモジュール
'''

def itemcopy(item):
    try:
        item.copy
    except AttributeError:
        return item
    else:
        return item.copy()

from singleton import *
from observer import *
