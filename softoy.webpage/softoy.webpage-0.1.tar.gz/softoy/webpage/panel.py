# -*- coding: utf-8 -*-
from selmod.htmltags.htmltags import Tag as T

def centering(length, parent_length):
    offset = (parent_length - length) / 2
    if offset >= 0:
        return offset
    else:
        return 0

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Panel(T):
    def __init__(self, x, y, **kw):
        super(Panel, self).__init__('div', **kw)
        self.x = x
        self.y = y
        self.width = kw.get('w', 100)  #?
        self.height = kw.get('h', 100)  #?
        self.w = kw.get('w', 100)
        self.h = kw.get('h', 100)
        self.style['left'] = self.px(self.x)
        self.style['top'] = self.px(self.y)
        self.style['width'] = self.px(self.w)
        self.style['height'] = self.px(self.h)
        self.attrs['class'] = 'abs'

    def px(self, n):
        if n is not None and type(n) == int:
            return '%spx' % n

    def reside_center(self, tag, width, height):
        x = centering(width, self.w)

