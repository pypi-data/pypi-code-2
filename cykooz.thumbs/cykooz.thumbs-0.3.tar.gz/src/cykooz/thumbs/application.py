# -*- coding: utf-8 -*-
'''
Created on 13.10.2010

@author: cykooz
'''
from middleware import make_thumbs
from paste.urlparser import StaticURLParser

def make_thumbs_app(global_config, **kwargs):
    document_root = kwargs.get('image_dir')
    if 'cache_max_age' in kwargs:
        cache_max_age = kwargs.pop('cache_max_age')
    else:
        cache_max_age = None
    application = StaticURLParser(document_root,
                                  cache_max_age=cache_max_age)
    return make_thumbs(application, global_config, **kwargs)

