# -*- coding: utf-8 -*-
'''
Created on 02.06.2009

@author: cykooz
'''

import os
import re
import time
import shutil
from cStringIO import StringIO

import webob
from paste.fileapp import FileApp
import zope.datetime

from image_processing import render_to_cache

DEPRICATED_SCALE_METHODS = {'crop': 'crop', 'scale_fit': 'fit_stretch', 'scale_stretch': 'stretch'}
SCALE_METHODS = ('crop', 'stretch', 'squash', 'fit_stretch', 'fit_squash')
DEFAULT_SIZE = {'size': (0, 0), 'scale_method': 'fit_stretch', 'quality': 75}


class Thumbs(object):
    def __init__(self, application, cache_dir, sizes, **kwargs):
        self.application = application
        self.cache_dir = cache_dir
        self.sizes = {}
        for k, v in sizes.items():
            if 'params' in sizes:
                print 'Dict item "params" is depricated, use "scale_method" instead'
                if sizes['params'] and sizes['params'][-1] in DEPRICATED_SCALE_METHODS:
                    sizes['scale_method'] = DEPRICATED_SCALE_METHODS[sizes['params'][-1]]
                del sizes['params']
            self.sizes[k] = DEFAULT_SIZE.copy()
            self.sizes[k].update(v)


    def get_file_in_cache_path(self, path_info, view, quality):
        path, file = os.path.split(path_info)
        file = '%s.%s' % (file, quality=='png' and 'png' or 'jpg')
        path = os.path.join(self.cache_dir, view, path.strip('/'))
        if not os.path.isdir(path):
            os.makedirs(path)
        return os.path.join(path, file)


    def __call__(self, environ, start_response):
        request = webob.Request(environ)

        # Проверяем подходит ли этот запрос для этого middleware
        if not (request.method == 'GET' and 
                ('view' in request.GET) and
                (request.GET['view'] == '__clear_cache__' or
                 request.GET['view'] in self.sizes)):
            return self.application(environ, start_response)
        
        view = request.GET['view']
        if view == '__clear_cache__':
            shutil.rmtree(self.cache_dir)
            return webob.Response('Cache cleared')(environ, start_response)
            
        size_info = self.sizes[view]
        cache_path = self.get_file_in_cache_path(request.path_info, view, size_info['quality'])
        in_cache = os.path.isfile(cache_path)
        
        response = None
        
        if in_cache:
            # Проверяем не изменилось ли исходное изображение
            ims = request.headers.get('If-Modified-Since', None) # Сохраняем значение заголовка If-Modified-Since
            mtime = os.stat(cache_path).st_mtime
            request.headers['If-Modified-Since'] = zope.datetime.rfc1123_date(mtime)
            del request.GET['view']
            response = request.get_response(self.application)
            if response.status == '404 Not Found':
                os.remove(cache_path)
                return response(environ, start_response)
            if response.status != '304 Not Modified':
                in_cache = False  
            # Востанавливаем значение заголовка
            if ims != None:
                request.headers['If-Modified-Since'] = ims
            else:
                del request.headers['If-Modified-Since']

        if not in_cache:
            # Get image from application and resize.
            if response == None:
                if 'If-Modified-Since' in request.headers:
                    # Нам необходимо получить картинку, а потому удаляем заголовок
                    del request.headers['If-Modified-Since']
                del request.GET['view']
                response = request.get_response(self.application)
            
            if not (response.content_type and 
                    response.content_type.startswith('image/')):
                return response(environ, start_response)
            
            app_iter = response.app_iter
            if not hasattr(app_iter, 'read'):
                app_iter = StringIO(''.join(app_iter))

            if 'Last-Modified' in response.headers:
                last_modified = response.headers['Last-Modified']
                last_modified = zope.datetime.time(last_modified)
            else:
                last_modified = time.time()
            
            render_to_cache(cache_path, last_modified, app_iter, size_info)

        return FileApp(cache_path)(environ, start_response)



PARSE_SIZE_RE = re.compile('(?P<width>\d+)x(?P<height>\d+)(?:,.*)?', re.I)
PARSE_PARAMS_RE = re.compile('(?:,([^,\sq]+))', re.I)
PARSE_QUALITY_RE = re.compile(',q((?:\d+)|(?:png))', re.I)

def parse_size(raw_size):
    '''
        Формат размера:
        <width>x<height>[,param][,param]...
        Параметры:
        q<quality> - качество сжатия JPEG (по умолчанию 75),
                    если quality=png то картинка упаковывается в PNG.
        crop - выполнять обрезание картики до заднного размера
        scale_<method> - метод масштабирования картинки до заданных размеров:
            fit - вписать картинку (по умолчанию)
            stretch - растянуть картинку
        Возвращает:
        (size, params)
            size - (<width>, <height>)
            params - [param, ...]
            quailty
    
        Пример:
        >>> parse_size('100x200,q80,crop')
        {'quality': 80, 'scale_method': 'crop', 'size': (100, 200)}
    '''
    size = PARSE_SIZE_RE.findall(raw_size)[0]
    size = tuple(map(int, size))
    size_info = {'size': size}
    params = PARSE_PARAMS_RE.findall(raw_size)
    for param in params:
        if param in SCALE_METHODS:
            size_info['scale_method'] = param
    quality = PARSE_QUALITY_RE.findall(raw_size)
    if not quality:
        size_info['quality'] = 75
    elif quality[0] != 'png':
        size_info['quality'] = int(quality[0])
    else:
        size_info['quality'] = 'png'
    return size_info


def make_thumbs(application, global_config, cache_dir=None, **kwargs):
    if not 'sizes' in kwargs:
        raise RuntimeError(u'Not defined parameter "sizes"')
    sizes = [v.strip() for v in kwargs['sizes'].split('\n')]
    sizes = [v.split('=') for v in sizes if v]
    sizes = [(k.strip(), parse_size(v)) for k, v in sizes]
    sizes = dict(sizes)
    del kwargs['sizes']

    return Thumbs(application, cache_dir, sizes, **kwargs)
