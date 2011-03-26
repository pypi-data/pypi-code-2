# -*- coding: utf-8 -*-
# Отдача статического контента средствами движка

import os

from names import fpath
from bottle import request, route, static_file

def maker(cfg, hook):

    @route('%s/favicon.ico' % cfg.prefix)
    @route('%s:filename#.*#' % 
           (cfg.prefix + cfg.staticUrl))
    def serve_static(filename='favicon.ico'):
        return static_file(filename.decode('utf-8'), root=fpath(cfg.staticRoot))

    @route('%s:filename' % 
            (cfg.prefix + cfg.attaches.pathUrl))
    def serve_static(filename='index.html'):
        return static_file(filename.decode('utf-8'), root=fpath(cfg.attaches.pathFs))

    @route('%s:filename' % 
            (cfg.prefix + cfg.attaches.thumbs.pathUrl))
    def serve_static(filename='index.html'):
        return static_file(filename.decode('utf-8'), root=fpath(cfg.attaches.thumbs.pathFs))

    return []


