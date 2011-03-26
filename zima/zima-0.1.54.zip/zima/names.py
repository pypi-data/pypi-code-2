# -*- coding: utf-8 -*-
# Имена и маршруты
import os
import random
from time import time

def uid():
    """ Красивые уникальные индексы """
    def dec(n, abc): 
        return n / len(abc), abc[n % len(abc)]
    num = random.getrandbits(32) + (long(time()) << 32)
    out = []
    while num > 0:
        num, sgl = dec(num, 'bcdfghklmnpqrstvwxz')
        num, gl = dec(num, 'aeijouy')
        out.extend([sgl, gl])
    return ''.join(out)

def fpath(l, name='', ext=''):
    " Абсолютный файловый маршрут "
    return os.path.abspath(os.path.join(*(map(unicode, l)+[name])))+ext

def uqpath(name, path='',  ext=''):
    """ Возвращает гарантированно уникальное имя файла в указанном
    каталоге"""
    guess = name
    i = 0
    while os.path.exists(fpath(path, guess, ext)):
        i += 1
        guess = '%s (%d)' % (name, i)
    return guess

def reflink(id, parent, prefix='', host='', proto='http', defhost=[]):
    """ Ссылка на сообщение """
    url = ''
    if host and host not in defhost:
        url += '%s://%s' % (proto, host)
    url += '%s/res/%s.html' % (prefix, parent)
    url += id and '#%s' % id or ''
    return url

def reftitle(host='', prefix='', num='', defaults=None):
    """ Надпись ссылки на сообщение"""
    if defaults and host in defaults['host']:
        host = ''
    if defaults and defaults['pfx'] == prefix:
        prefix = ''
    if prefix <> '' and prefix[-1] <> '/':
        prefix += '/'
    return '>>%s%s%s' % (host, prefix, num)