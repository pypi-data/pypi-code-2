# -*- coding: utf-8 -*-
from pysi import cfg
from util import anticache_headers


cfg.set_defaults(
    BASIC_AUTH_PREFIXES = ('/', ),
    ANTICACHE_PREFIXES = ('/', ),
)

def basic_auth_middleware(rq):
    '''Basic-auth request middleware'''
    if rq.path.startswith(cfg.BASIC_AUTH_PREFIXES):
        rq.basic_user

def anticache_middleware(rq, res):
    '''Browser anti-cache response middleware'''
    if rq.path.startswith(cfg.ANTICACHE_PREFIXES):
        res.headers.update(anticache_headers())

