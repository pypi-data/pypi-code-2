# -*- coding: utf-8 -*-
'''
Роутинг
'''
import urllib
import datetime

from exceptions import NotFound
from config import cfg
import wsgi


class UrlMap(object):
    url_prefix = None
    tree = []
    rev = {}
    
    def add_rule(self, url, target, name=None):
        if self.url_prefix:
            url = '/%s/%s' % (self.url_prefix, url.lstrip('/'))
        dirs = url.split('/')[1:]
        cur = self.tree
        vars = []
        rev_chunks = ['']
        for i, dir in enumerate(dirs):
            raw_dir = dir
            if dir.startswith('<') and dir.endswith('>'):
                dir, var = dir[1:-1].split(':')
                rev_chunks.append(REVERSES[dir](var))
                dir = '<%s>' % dir
                vars.append(var)
            else:
                rev_chunks.append(dir)
            node = dict(cur).get(dir)
            if not node:
                node = {
                    'target': None,
                    'next': [],
                    'match': get_match(raw_dir),
                    'vars': vars,
                }
                cur.append((dir, node))
            if i == len(dirs) - 1 and node['target'] is None:
                # последняя папка
                node['target'] = target
            cur = node['next']
        if name:
            self.rev.setdefault(name, []).append(
                ('/'.join(rev_chunks), vars))
                
    def reverse(self, *args, **kwargs):
        name = args[0]
        for tpl, vars in self.rev.get(name):
            for k in vars:
                if k not in kwargs:
                    break
            else:
                try:
                    url = urllib.quote(tpl % kwargs)
                except (TypeError, KeyError):
                    pass
                else:
                    # GET параметры
                    if len(kwargs) > len(vars):
                        ext_vars = {}
                        for k, v in kwargs.iteritems():
                            if k not in vars:
                                if isinstance(v, unicode):
                                    v = v.encode(cfg.CHARSET)
                                ext_vars[k] = v
                        if ext_vars:
                            url += '?' + urllib.urlencode(ext_vars)
                    return url
    
    def find(self, url):
        dirs = url.split('/')[1:]
        cur = self.tree
        res = None, {}
        vals = []
        i = 0
        while i < len(dirs):
            for d, node in cur:
                match, val = node['match'](dirs[i])
                if match:
                    if val is not None:
                        if val == '<//__slug__//>':
                            vals.append('/'.join(dirs[i:]))
                            i = len(dirs) - 1
                        else:
                            vals.append(val)
                    break
            else:
                break
            cur = node['next']
            i += 1
        else:
            vars = dict((node['vars'][i], vals[i])
                for i in xrange(len(vals))) if vals else {}
            res = node['target'], vars
        return res
        
def match_const(var):
    return lambda dir: (dir == var, None)

def match_str(var):
    return lambda dir: (True, urllib.unquote_plus(dir))
    
def match_int(var):
    def f(dir):
        if dir.isdigit():
            return True, int(dir)
        else:
            return False, None
    return f

def match_date(var):
    def f(dir):
        try:
            dt = datetime.datetime.strptime(dir, '%Y-%m-%d')
        except:
            return False, None
        return True, datetime.date(dt.year, dt.month, dt.day)
    return f

def match_slug(var):
    return lambda dir: (True, '<//__slug__//>')


MATCHS = {
    'int': match_int,
    'str': match_str,
    'date': match_date,
    '*': match_slug,
}

def get_match(dir):
    if dir.startswith('<') and dir.endswith('>'):
        name = dir[1:-1]
        name, var = name.split(':')
        func = MATCHS.get(name)
        if func:
            return func(dir)
    return match_const(dir)

REVERSES = {
    'int': lambda var: '%%(%s)i' % var,
    'str': lambda var: '%%(%s)s' % var,
    'date': lambda var: '%%(%s)s' % var,
    '*': lambda var: '%%(%s)s' % var,
}


#######################
### Привязка к pysi ###
#######################
urls = UrlMap()

def auto_routing(rq):
    '''
    Автоматический роутинг
    '''
    func, kwargs = urls.find(rq.path)
    if func is None:
        if not rq.path.endswith('/'):
            # забыли закрывающий слеш?
            func, kwargs = urls.find(rq.path + '/')
            if func:
                return wsgi.redirect(rq.path + '/')        
        raise NotFound
    return func(rq, **kwargs)
    
def add_urls(*rules):
    ''' Добавление правил списком'''
    for rule in rules:
        urls.add_rule(*rule)
        
def url4(*args, **kwargs):
    return urls.reverse(*args, **kwargs)
    
def add_apps(apps):
    '''
    Добавление приложений
        apps = ['mod1', ('mod2', url_prefix), 'mod3']
    '''
    for mod in apps:
        if isinstance(mod, tuple):
            mod, prefix = mod
            urls.url_prefix = prefix.strip().strip('/') or None
        app_name = '%s.%s' % (mod, 'views')
        __import__(app_name)
        urls.url_prefix = None
