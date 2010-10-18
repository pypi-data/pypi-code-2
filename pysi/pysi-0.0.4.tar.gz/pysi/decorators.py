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

def as_response(**response_kwargs):
    ''' Базовый декоратор response '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            return Response(func(*args, **kwargs), **response_kwargs)
        return wrapper
    return decorator
    
def as_text(**kwargs):
    ''' Декоратор текстовый response '''
    return as_response(content_type='text/plain', **kwargs)
    
def as_html(**kwargs):
    ''' Декоратор html-response '''
    return as_response(content_type='text/html', **kwargs)

def as_json(**response_kwargs):
    ''' Декоратор json_response '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'content_type' not in response_kwargs:
                response_kwargs['content_type'] = 'application/json'
            return Response(json.dumps(func(*args, **kwargs),
                default=lambda v: 'no json serializable'), **response_kwargs)
        return wrapper
    return decorator

def to_template(fn, **response_kwargs):
    '''
    Декоратор шаблонизации
    '''
    def decorator(func):
        def wrapper(rq, *args, **kwargs):
            return render_to_response(
                rq, fn, func(rq, **kwargs), **response_kwargs)
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
