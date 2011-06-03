# -*- coding: utf-8 -*-
"""
htmltags.py
"""

from selmod.tree.tree import Node
from webhelpers.html import literal

def deprecate(name):
    print '%s.%s is DEPRECATED.' % (__name__, name)

# tag categories
EmptyTags = ['br', 'hr', 'input', 'link', 'meta']

# attribute categories
AllowEmptyStringAttributes = ['action']

DocType = {
    'H_4.01_S': '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
    ''',

    'H_4.01_T': '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
    "http://www.w3.org/TR/html4/loose.dtd">
    ''',

    'H_4.01_F': '''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN"
    "http://www.w3.org/TR/html4/frameset.dtd">
    ''',

    'X_1.0_S':'''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    ''',

    'X_1.0_T':'''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    ''',

    'X_1.0_F':'''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">
    '''

    }

def warn_deprecate(module, location, substitute, *args):
    message = ''
    if args:
        message = ' - %s' % args[0]
    print '%s: %s is DEPRECATED use %s%s' % (
        module, location, substitute, message)

def attrs_cond(x, **kw):
    for k, v in kw.items():
        if k not in x.attrs:
            return False
        else:
            if x.attrs[k] != kw.get(k):
                return False
    return True


class Tag(Node):
    basic_attributes = ['dir', 'id', 'lang', 'title', 'xml:lang', 'accesskey', 'tabindex',
        'onclick']
        
    def __init__(self, tag, **kw):
        name = kw.get('name')
        span = kw.get('span')
        as_root = kw.get('as_root')
        super(Tag, self).__init__(name, span=span, as_root=as_root)

        self.tag = tag  # html tag
        self.attrs = kw.get('attrs', {})
        self.doctype = kw.get('doctype', 'H_4.01_T')

        # setting HTML standard attributes except style
        self.attrs.update(dict([(a, kw[a])
            for a in Tag.basic_attributes if kw.get(a) is not None]))
        class_ = kw.get('class_')
        if class_:
            self.attrs['class'] = class_

        # XHTML
        self.xml_version = kw.get('xml_version', '1.0')
        self.xml_encoding = kw.get('xml_encoding', 'UTF-8')
        if self.tag == 'html' and self.is_xhtml():
            self.attrs['xmlns'] = 'http://www.w3.org/1999/xhtml'
            if 'lang' not in self.attrs:
                self.attrs['lang'] = 'en'
            if 'xml:lang' not in self.attrs:
                self.attrs['xml:lang'] = 'en'

        self.style = kw.get('style', {})
        self.data = kw.get('data')
        self.events = kw.get('events')
        self.js = kw.get('js')
        self.styles = kw.get('styles', '')

        self.no_end_tag = False
        self.no_child = False
        if self.attrs is None:
            self.attrs = {}
        if self.style is None:
            self.style = {}
        if self.styles:
            self.set_styles()
        children = kw.get('children')
        if children:
            self.be_children(children)
        self.styleup = kw.get('styleup')
        if self.styleup:
            self.style.update(self.styleup)
        self.attrsup = kw.get('attrsup')
        if self.attrsup:
            self.attrs.update(self.attrsup)


    def __str__(self):
        if self.sup:
            sup_is = 'yes'
        else:
            sup_is = 'NO'

        if self.indexer:
            indexer_is = 'yes'
        else:
            indexer_is = 'NO'
        return 'name:%s tag:%s sup:%s indexer:%s' % (
            self.name, self.tag, sup_is, indexer_is)

    def is_xhtml(self):
        return  self.doctype[0] == 'X'

    def doctype_text(self):
        if not self.is_xhtml():
            return DocType[self.doctype]
        else:
            XML_declaration = '<?xml version="%s" encoding="%s"?>' % (
                self.xml_version, self.xml_encoding)
            return '%s\n%s\n' % (XML_declaration, DocType[self.doctype])

    def travel(self, tags=None):
        if tags is None:
            tags = self.doctype_text()
        if self.subs:
            tag = self.make_tag()
            tags += tag[0] + u'\n'   # tag open
            for sub in self.subs:
                if isinstance(sub, Tag):
                    tags += sub.travel(tags='')
            tags += tag[1] + u'\n'   # tag close
        else:
            if not hasattr(self, 'extend'):
                L = [self]
            else:
                L = self.extend()
            for e in L:
                if isinstance(e, Tag):
                    tag = e.make_tag()
                    tags += tag[0]
                    tags += tag[1] + u'\n'
        return tags

    def render(self):
        return literal(self.travel())

    def double_quotes(self, s):
        return '"%s"' % s

    def make_attr(self, name, val):
        if not val:
            return ''
        if type(val) != str:
            s = str(val)
        else:
            s = val
        return name + u'=' + self.double_quotes(s)


    def attrs_has_key(self, k):
        return self.attrs.has_key(k)


    def make_attrs(self):
        def available_attr_conditions(k, v):
            if k in AllowEmptyStringAttributes:
                if v or v == '':
                    return True
            else:
                if v:
                    return True
            return False

        result = []
        for k,  v in self.attrs.items():
            if k == 'class_':
                k = 'class'
            elif k == '_class':
                k = 'class'
            elif k == 'type_':
                k = 'type'
            elif k == '_type':
                k = 'type'

            if available_attr_conditions(k, v):
                if type(v) != unicode:
                    v = unicode(v)
                if v == '':
                    v = self.double_quotes('')
                elif v[0]  != u'"' or v[0] != u"'":
                    v = self.double_quotes(v)
            else:
                v = self.double_quotes('')
            result.append(k + '=' + v)
        return result

    def make_style_attrs(self):
        result = []
        if self.style:
            for n, v in self.style.items():
                result.append(n + u':%s' % v)
        return result

    def set_styles(self):
        declarations = self.styles.split(';')
        for dec in declarations:
            if dec:
                pv_pair = dec.split(':')
                self.style[pv_pair[0]] = pv_pair[1]

    def make_tag(self):
        if not self.is_xhtml() and self.tag in EmptyTags:
            self.no_end_tag = True
        else:
            self.no_end_tag = False
        if self.tag in EmptyTags:
            self.no_child = True
        attrs = self.make_attrs()
        style_attrs = self.make_style_attrs()
        style = ';'.join(style_attrs)
        attrs.append((self.make_attr('style', style)))

        if self.no_child:
            if self.no_end_tag and not self.is_xhtml():
                tag_open = u'<%s %s>' % (self.tag, u' '.join(attrs))
            else:
                tag_open = u'<%s %s/>' % (self.tag, u' '.join(attrs))
            return [tag_open, '']
        else:
            tag_open = u'<%s %s>' % (self.tag, u' '.join(attrs))

            if self.data:
                tag_data = self.data
            else:
                tag_data = ''

            tag_close = u'%s</%s>' % (tag_data, self.tag)
            return [tag_open, tag_close]


    def visit(self, cond=lambda x: True, applyer=lambda x:x, L=[],
        cond_kw={}, applyer_kw={}):
        if cond(self, **cond_kw):
            L.append(applyer(self, **applyer_kw))
        for sub in self.subs:
            L = sub.visit(cond=cond, applyer=applyer, L=L,
                cond_kw=cond_kw, applyer_kw=applyer_kw)
        return L


    def visit2(self, applyer=lambda x:x, L=[], cond=lambda x: True,
        cond_kw={}, applyer_kw={}):
        result = applyer(self, **applyer_kw)
        if cond(result, **cond_kw):
            L.append(result)
        for sub in self.subs:
            L = sub.visit2(cond=cond, applyer=applyer, L=L,
                cond_kw=cond_kw, applyer_kw=applyer_kw)
        return L


    def __getitem__(self, others):
        if not isinstance(others, (tuple, list)):
            others = (others,)
        for o in others:
            if o is not None:    # deleting empty tag
                self.subs.append(o)
                o.sup = self
                o.indexer = self.indexer
        return self

    def multi_append(self, others):
        return self.__getitem__(others)

    def clear_subs(self):
        self.subs = []

    def selector(self, **kw):
        if 'class_' in kw:
            v = kw['class_']
            kw['class'] = v
            del kw['class_']
        return self.visit(cond=attrs_cond, cond_kw=kw)


def empty_doc(**kw):
    head = Tag('head')
    body = Tag('body')
    html = Tag('html', **kw)[head, body]
    return html, head, body

def setup_name_indexer(x, indexer):
    try:
        if x.name:
            indexer.register(x.name, x)
        x.indexer = indexer
    except AttributeError:
        pass
