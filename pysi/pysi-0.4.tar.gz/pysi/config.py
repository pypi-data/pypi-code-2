# -*- coding: utf-8 -*-
import wsgi


class Cfg(object):
    DEBUG = False
    BASIC_AUTH_SSL_ONLY = True  # basic-авторизация только по https
    BASIC_AUTH_DB = {}
    INSTALLED_APPS = []
    CONTEXT_PROCESSORS = []
    REQUEST_MIDDLEWARES = []
    RESPONSE_MIDDLEWARES = []
    CHARSET = 'utf-8'
    POST_MAX_SIZE = 1024 * 1024 * 1  # максимальный размер пост-данных, None - не ограничивать
    POST_MAX_MEMFILE = 1024 * 100  # максимальный размер POST-данных, загружаемый в память. Если больше, создаётся временный файл.
    ERROR_PAGES = {
        404: lambda rq: wsgi.Response(wsgi.HTML_404, code=404, content_type='text/html'),
        500: lambda rq: wsgi.Response(wsgi.HTML_500, code=500, content_type='text/html'),
    }
    TEMPLATE_CACHE_SIZE = 250
    TEMPLATE_AUTO_RELOAD = False
    TEMPLATE_LOADER = 'pysi.template.file_loader'
    FLASH_COOKIE_NAME = u'pysi.flash'
    ROUTING = 'pysi.auto_routing'  # функция или очередь функция роутинга

    def set_defaults(self, **kwargs):
        '''
        Добавляем дефолтные атрибуты
        '''
        for k, v in kwargs.iteritems():
            if not hasattr(self, k) and k.isupper():
                setattr(self, k, v)

cfg = Cfg()
