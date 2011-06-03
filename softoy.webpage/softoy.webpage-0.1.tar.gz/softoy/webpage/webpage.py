# -*- coding: utf-8 -*-
from selmod.htmltags.htmltags import Tag as T
from selmod.widgets import widgets as w

class Carry:
    pass


class WebPage(object):
    def __init__(self, c, **kw):
        self.c = c
        self.width = kw.get('width', 940)
        self.title = kw.get('title', '')
        self.css = kw.get('css', '')
        self.font_size = kw.get('font_size', '16px')
        self.page_title = T('title', data=self.title)
        self.head = w.Head()
        self.body = w.Body()
        self.root = w.Html()[self.head, self.body]
        self.foot_script = kw.get('foot_script')
        self.body.style={'text-align':'center', 'font-size':self.font_size}
        self.head[
            T('meta', attrs={'http-equiv':'Content-Type',
                'content':'text/html; charset=utf-8'}),
            self.page_title,
            ]
        if self.css:
            self.head.append(T('style', attrs={'type':'text/css'}, data=self.css))
        stylesheet_url = kw.get('stylesheet_url')
        if stylesheet_url:
            self.head.append(w.Stylesheet(url=stylesheet_url))
        self.cshell = T('div', id='cshell', styleup={'width':'%spx' % self.width})
        self.body[self.cshell]

    def render(self):
        self.root.set_head_tags(self.head)
        self.cshell.append(self.foot_script)
        return T.render(self.root)

    def set_title(self, title):
        self.page_title.data = title


class Redirect(object):
    def __init__(self, url):
        self.head = w.Head()
        self.body = w.Body()
        self.root = w.Html()[self.head, self.body]
        self.head[
            T('meta', attrs={'http-equiv':'REFRESH', 'content':'0;url=%s' % url})
            ]
            
    def render(self):
        return T.render(self.root)
        



