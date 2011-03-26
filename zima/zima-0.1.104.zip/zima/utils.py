# -*- coding:utf-8 -*-
# Различные утилитарные классы и функции

from itertools import chain

import os
import random
from time import time
import logging

# Немножко функциональщины
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

# TODO: Добавить поддержку kwargs
def currydef(fun, *args):
    "Переписывает значения аргументов по умолчанию"
    def f(*cargs):
        dargs = list(args)
        for i in range(0, len(cargs)):
            if cargs[i] <> None:
                dargs[i] = cargs[i]
        return fun(*dargs)
    return f

# Штуки для конфига
class AttrWrapper():
    """ Преобразует словарь в объект с атрибутами c учетом
    вложенности.

    Вложенность учитывается следующим образом: если любой из дочерних
    объектов словарь - он также становится attWrapper'ом."""

    def __init__(self, dict):
        for k, v in dict.items():
            def val(v):
                if v.__class__.__name__ == 'dict' and not k[0] == '_':
                    return AttrWrapper(v)
                else:
                    return v

            if v.__class__.__name__ == 'list':
                setattr(self, k,  map(val, v))
            else:
                setattr(self, k, val(v))


def derive(parent, mutations):
    """ Функция реализующая 'наследование' для словарей со всеми
    встроенными причиндалами.

    Наследование осуществляется по следующим правилам:

    1. Если в ключ присутствует в дочернем и родительском словаре,
    дочерний ключ переписывает родительский. Однако если эти ключи
    словари - то происходит не переписывание, а рекурсивный вызов
    derive.

    2. Если ключ присутствует только в родительском словаре либо в
    дочернем словаре, то он добавляется в результирующий.

    Примеры:

    derive({'a':1}, {'b':2}) => {'a':1, 'b':2}

    derive({'foo': True, 'bar':{'baz':'origin'}}, {'bar':{'bazz':1}} =>
    => {'foo':True, 'bar':{'baz':'origin', 'bazz':1}}"""
    try:
        child = parent.copy()
    except:
        child = {}

    # Apply our mutations recursively
    for k, v in mutations.items():
        def val(v, orig):
            if v.__class__.__name__ == 'dict':
                return derive(orig, v)
            else:
                return v

        if k in child:
            child[k] = val(v, child[k])
        else:
            child[k] = v

    return child


#------------------------------------------------------------------
# Поточный бассейн

class ThreadPool:
    from Queue import Queue

    q = Queue()
    pipeline = None

    log_i = 0

    def _start(self):
        from threading import Thread
        def closure():
            self.q.join()
            self.pipeline = None
        if not self.pipeline:
            self.pipeline = Thread(target=closure)
            self.pipeline.start()

    def __init__(self, workersCount):
        from threading import Thread

        def worker():
            while True:
                func, args, kargs = self.q.get()
                try:
                    func(*args, **kargs)
                except Exception, e:
                    print e
                self.q.task_done()

                self.log_i += 1
                self.log_i %= 100
                if self.log_i == 0 and self.q.qsize() > workersCount * 5:
                    logging.warning(
                        'Task queue goes fat (%d)' % self.q.qsize())

        for i in range(workersCount):
            t = Thread(target=worker)
            t.setDaemon(True)
            t.start()

    def schedule(self, func, *args, **kwargs):
        self.q.put((func, args, kwargs))
        self._start()



#------------------------------------------------------------------
# Перевод

def _n_en(n, tr_dict):
    """ Plural numeric, ngettext analog """
    return  n == 1 and tr_dict[0] or tr_dict[1]

def _sz_c(trDict, divisor, _n):
    """ Plural sizes """
    divisor = divisor * 1.0 # Make em float
    def f(size):
        arg = 0
        while size / divisor >= 1:
            arg += 1
            size = size / divisor
        if arg == 0:
            return '%s%s' % (size, _n(size, trDict[arg]))
        else:
            return '%1.1f%s' % (size, _n(size, trDict[arg]))
    return f
