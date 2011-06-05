# -*- coding: utf-8 -*-
from softoy.htmltags.htmltags import Tag as T
import formencode
from formencode import validators, Schema
from formencode.validators import String, PlainText

class Bus: pass
bus = Bus()
bus.page_css = 'page_css'
another_css_data = 'another_css_data'
bus.upper_scripts = 'upper_scripts'
bus.lower_scripts = 'lower_scripts'

def set_indexer(o, indexer):
    o.indexer = indexer

def test0():
    html = T('html', as_root=True)
    html[
        T('head', name='head')[
            T('script', name='upper_scripts', data=bus.upper_scripts),
        ], # head
        T('body', name='body')[
            T('div', name='outer', attrs=dict(id='outer')),
            T('script', name='lower_scripts', data=bus.lower_scripts),
        ] # body
    ] # html

    print html.subs
    #head = html.search('head')

from Queue import Queue

class Display(object):
    def __init__(self, name):
        self.name = name
        self.subs =[]

    def __call__(self):
        print 'name: %s' % self.name

def bft(T, Q):
    x = T.pop(0)
    Q.put(x)

    while True:
        y = Q.get()
        y()
        for z  in y.subs:
            Q.put(z)

        if Q.empty():
            return

def test_queue():
    Q = Queue(100)
    bft(T, Q)

def test():
    page = T('div', id='page')[
        T('p', id='header'),
        T('p', id='main', class_='target'),
        T('span', id='footer', class_='target'),
        ]
    L = page.selector(id='footer', class_='target')
    print 'L', [str(x) for x in L]

test()


