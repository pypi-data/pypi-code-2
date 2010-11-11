# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    from django.utils import simplejson as json

from wsgi import Response
from exceptions import BasicAuth, Redirect
from routing import urls
from config import cfg
from util import anticache_headers
from template import render_to_response


def route(url, name=None):
    ''' Декоратор роутинга '''
    def wrapper(func):
        urls.add_rule(url, func, name)
        return func
    return wrapper

def as_response(dumper=None, **response_kwargs):
    ''' Базовый декоратор response '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if not isinstance(res, Response):
                if dumper:
                    res = dumper(res)
                res = Response(res, **response_kwargs)
            return res
        return wrapper
    return decorator
    
def as_text(**kwargs):
    ''' Декоратор текстовый response '''
    return as_response(content_type='text/plain', **kwargs)
    
def as_html(**kwargs):
    ''' Декоратор html-response '''
    return as_response(content_type='text/html', **kwargs)

def as_json(**kwargs):
    ''' Декоратор json_response '''
    return as_response(dumper=json.dumps,
        content_type='application/json', **kwargs)

def to_template(fn, **response_kwargs):
    '''
    Декоратор шаблонизации
    '''
    def decorator(func):
        def wrapper(rq, *args, **kwargs):
            res = func(rq, *args, **kwargs)
            if isinstance(res, Response):
                return res
            return render_to_response(
                rq, fn, res, **response_kwargs)
        return wrapper
    return decorator

def anticache(func):
    ''' Декоратор браузерного антикэша '''
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        res.headers.update(anticache_headers())
        return res
    return wrapper

def error(code):
    ''' Декоратор страницы ошибки '''
    def wrapper(func):
        cfg.ERROR_PAGES[code] = func
        return func
    return wrapper

def basic_auth(func):
    '''
    Basic-авторизация.
    '''
    def wrapper(rq, *args, **kwargs):
        rq.basic_user
        return func(rq, *args, **kwargs)
    return wrapper
