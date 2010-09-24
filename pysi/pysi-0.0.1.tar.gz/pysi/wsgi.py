# -*- coding: utf-8 -*-
import cgi
import logging
from hashlib import sha1
from StringIO import StringIO
from tempfile import TemporaryFile
from Cookie import SimpleCookie

from util import cache_property, make_traceback, list_obj_from_str
from config import cfg
from exceptions import NotFound, Redirect, PermanentRedirect, BasicAuth
from routing import auto_routing, add_apps
from multidict import MultiDict, HeaderDict


class Request(object):
    charset = 'utf-8'
    encoding_errors = 'ignore'
    max_post_size = None  # максимальный размер post-данных
    
    def __init__(self, environ):
        self.environ = environ
        self.path = environ['PATH_INFO'].decode(self.charset, self.encoding_errors)
    
    @cache_property
    def context(self):
        res = {}
        for func in cfg.CONTEXT_PROCESSORS:
            res.update(func(self))
        return res

    @cache_property
    def method(self):
        return self.environ['REQUEST_METHOD'].upper()

    @cache_property
    def GET(self):
        return MultiDict((k.decode(self.charset, self.encoding_errors),
            v[-1].decode(self.charset, self.encoding_errors))
                for k, v in cgi.parse_qs(self.environ['QUERY_STRING']).iteritems())
        
    @cache_property
    def POST(self):
        '''
        Данные POST-запроса.
        Строковые данные декодируются.
        Файлы:
            rq.POST['datafile'].file.read()  # содержимое файла
            rq.POST['datafile'].filename  # имя файла
        '''
        post = MultiDict()
        if self.method == 'POST':
            # создаём файловый объект в памяти или на диске в зависимости от размера
            try:
                maxread = int(self.environ.get('CONTENT_LENGTH', 0))
            except ValueError:
                maxread = 0
            if self.max_post_size and maxread > self.max_post_size:
                assert 0, 'big post data size'
            stream = self.environ['wsgi.input']
            if cfg.POST_MAX_MEMFILE is None or maxread < cfg.POST_MAX_MEMFILE:
                body = StringIO()
            else:
                body = TemporaryFile(mode='w+b')
            while maxread > 0:
                part = stream.read(min(maxread, cfg.POST_MAX_MEMFILE))
                if not part:  # TODO: Wrong content_length. Error? Do nothing?
                    break
                body.write(part)
                maxread -= len(part)
            body.seek(0)
            # обрабатываем этот объект
            safe_env = {'QUERY_STRING' : ''}  # Build a safe environment for cgi
            for key in ('REQUEST_METHOD', 'CONTENT_TYPE', 'CONTENT_LENGTH'):
                if key in self.environ: safe_env[key] = self.environ[key]
            data = cgi.FieldStorage(fp=body, environ=safe_env, keep_blank_values=True)
            for item in data.list or []:
                if item.filename:
                    post[item.name] = item  # файл
                else:
                    post[item.name] = item.value.decode(self.charset, self.encoding_errors)
        return post

    @cache_property
    def COOKIES(self):
        return SimpleCookie(self.environ.get('HTTP_COOKIE', ''))

    @cache_property
    def scheme(self):
        return self.environ.get('HTTP_X_SCHEME',
            self.environ.get('wsgi.url_scheme', 'http'))

    @cache_property
    def host(self):
        host = self.environ.get('HTTP_X_FORWARDED_HOST',
            self.environ.get('HTTP_HOST', None))
        if not host:
            host = self.environ.get('SERVER_NAME', '')
            port = self.environ.get('SERVER_PORT', '80')
            if self.scheme + port not in ('https443', 'http80'):
                host += ':' + port
        return host

    @cache_property
    def full_path(self):
        qs = self.environ.get('QUERY_STRING', '')
        return '%s?%s' % (self.path, qs) if qs else self.path

    @cache_property
    def url(self):
        '''Полный урл'''
        return '%s://%s%s' % (self.scheme, self.host, self.full_path)
            
    @cache_property
    def ip(self):
        return self.environ.get('HTTP_X_FORWARDED_FOR', self.environ.get(
            'HTTP_X_REAL_IP', self.environ.get('REMOTE_ADDR')))

    @cache_property
    def referer(self):
        return self.environ.get('HTTP_REFERER', '')
        
    @cache_property
    def user_agent(self):
        return self.environ.get('HTTP_USER_AGENT', '')
    
    @cache_property
    def basic_user(self):
        if cfg.BASIC_AUTH_SSL_ONLY and self.scheme != 'https':
            raise Redirect('https://%s%s' % (self.host, self.full_path))
        auth = self.environ.get('HTTP_AUTHORIZATION')
        if not auth:
            raise BasicAuth
        scheme, data = auth.split(None, 1)
        if scheme.lower() != 'basic':
            raise BasicAuth
        data = data.decode('base64').split(':', 1)
        if len(data) != 2:
            raise BasicAuth
        user, passwd = data
        if cfg.BASIC_AUTH_DB.get(user) != sha1(passwd).hexdigest():
            raise BasicAuth
        return user



class Response(object):
    code = 200  # дефолтный код ответа
    charset = 'utf-8'  # дефолтная кодировка
    encodeg_errors = 'ignore'
    content_type = 'text/html'  # дефолтный Content-Type
    
    def __init__(self, body='', headers=None, cookies=None, **kwargs):
        '''
        Response
            *body           - (str | unicode) тело ответа
            **code          - (int) код ответа
            **charset       - (str) кодировка страницы
            **content_type  - (str) Content-Type
            **headers       - (dict | items | iteritems) заголовки
            **cookies       - (list) куки
        '''
        self.__dict__.update(kwargs)
        self.body = body
        self.COOKIES = SimpleCookie()
        self.headers = HeaderDict(headers or {})
        if cookies:
            for cookie in cookies:
                self.set_cookie(**cookie)

    def set_cookie(self, key, val, **kwargs):
        """
        Устанавливаем куку:
            *key        - (unicode) ключ
            *val        - (unicode) значение
            **expires   - (int) время жизни куки в секундах, дефолт - до закрытия браузера
            **path      - (unicode) uri, '/' - для действия на весь домен
            **domain    - (unicode) дефолт - текущий поддомен, '.site.name' - для всех поддоменов
        """
        self.COOKIES[key.encode(self.charset, self.encodeg_errors)] = val.encode(self.charset, self.encodeg_errors)
        for k, v in kwargs.iteritems():
            self.COOKIES[key][k] = v

    def wsgi(self):
        '''
        Возвращает переменные wsgi-ответа: status, headers и body
        '''
        status = '%i %s' % (self.code, HTTP_CODES.get(self.code, 'Unknown'))
        if isinstance(self.body, unicode):
            self.body = self.body.encode(self.charset, self.encodeg_errors)
        else:
            self.body = str(self.body)
        # добавляем куки в заголовки
        cur_cooks = self.headers.getall('Set-Cookie')
        for c in self.COOKIES.itervalues():
            if c.OutputString() not in cur_cooks:
                self.headers.append('Set-Cookie', c.OutputString())
        # Content-Type
        if self.content_type in ['text/plain', 'text/html']:
            self.headers['Content-Type'] = '%s; charset=%s' % (
                self.content_type, self.charset)
        else:
            self.headers['Content-Type'] = self.content_type
        self.headers['Content-Length'] = str(len(self.body))
        
        return status, list(self.headers.iterallitems()), [self.body]
        
            
class App(object):
    def __init__(self, cfg_module=None, routing=None):
        '''
            *cfg_module - модуль конфигурации
            **routing   - функция роутинга
        '''
        self.routing = routing or auto_routing
        if cfg_module:
            for k in cfg_module.__dict__.keys():
                if not k.startswith('__') and k.isupper():
                    setattr(cfg, k, getattr(cfg_module, k))
        Request.charset = cfg.CHARSET
        Request.max_post_size = cfg.POST_MAX_SIZE
        Response.charset = cfg.CHARSET
        add_apps(cfg.INSTALLED_APPS)
        
        list_obj_from_str(cfg.CONTEXT_PROCESSORS)
        list_obj_from_str(cfg.REQUEST_MIDDLEWARES)
        list_obj_from_str(cfg.RESPONSE_MIDDLEWARES)

    def __call__(self, environ, start_response):
        rq = Request(environ)
        try:
            for middleware in cfg.REQUEST_MIDDLEWARES:
                middleware(rq)
            res = self.routing(rq)
            if not isinstance(res, Response):
                res = Response(unicode(res), content_type='text/plain')
            for middleware in cfg.RESPONSE_MIDDLEWARES:
                middleware(rq, res)
        except NotFound, e:
            if cfg.DEBUG:
                res = Response(make_traceback(rq.host),
                    code=404, content_type='text/plain')
            else:
                res = cfg.ERROR_PAGES[404](rq)
        except (Redirect, PermanentRedirect, BasicAuth), e:
            res = e.res
        except:
            tb = make_traceback(rq.host)
            logging.error(tb)
            if cfg.DEBUG:
                res = Response(tb, code=500, content_type='text/plain')
            else:
                res = cfg.ERROR_PAGES[500](rq)
        status, headers, body = res.wsgi()
        start_response(status, headers)
        return body


HTTP_CODES = {
    100:    'Continue',
    101:    'Switching Protocols',
    102:    'Processing',
    200:    'OK',
    201:    'Created',
    202:    'Accepted',
    203:    'Non Authoritative Information',
    204:    'No Content',
    205:    'Reset Content',
    206:    'Partial Content',
    207:    'Multi Status',
    226:    'IM Used',              # see RFC 3229
    300:    'Multiple Choices',
    301:    'Moved Permanently',
    302:    'Found',
    303:    'See Other',
    304:    'Not Modified',
    305:    'Use Proxy',
    307:    'Temporary Redirect',
    400:    'Bad Request',
    401:    'Unauthorized',
    402:    'Payment Required',     # unused
    403:    'Forbidden',
    404:    'Not Found',
    405:    'Method Not Allowed',
    406:    'Not Acceptable',
    407:    'Proxy Authentication Required',
    408:    'Request Timeout',
    409:    'Conflict',
    410:    'Gone',
    411:    'Length Required',
    412:    'Precondition Failed',
    413:    'Request Entity Too Large',
    414:    'Request URI Too Long',
    415:    'Unsupported Media Type',
    416:    'Requested Range Not Satisfiable',
    417:    'Expectation Failed',
    418:    'I\'m a teapot',        # see RFC 2324
    422:    'Unprocessable Entity',
    423:    'Locked',
    424:    'Failed Dependency',
    426:    'Upgrade Required',
    449:    'Retry With',           # propritary MS extension
    500:    'Internal Server Error',
    501:    'Not Implemented',
    502:    'Bad Gateway',
    503:    'Service Unavailable',
    504:    'Gateway Timeout',
    505:    'HTTP Version Not Supported',
    507:    'Insufficient Storage',
    510:    'Not Extended'
}

STATUS_HTML = '''<html>\n<head><title>%(code)s %(status)s</title></head>
<body bgcolor="white">\n<center><h1>%(code)s %(status)s</h1></center>
<hr><center>nginx/0.6.32</center>\n</body>\n</html>'''
HTML_404 = STATUS_HTML % {'code': 404, 'status': HTTP_CODES[404]}
HTML_500 = STATUS_HTML % {'code': 500, 'status': HTTP_CODES[500]}
