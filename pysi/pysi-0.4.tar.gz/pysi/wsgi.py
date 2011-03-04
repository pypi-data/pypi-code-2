# -*- coding: utf-8 -*-
import cgi
import logging
import marshal
import base64
from hashlib import sha1
from StringIO import StringIO
from tempfile import TemporaryFile
from Cookie import SimpleCookie

from util import cached_property, make_traceback, obj_from_str, list_obj_from_str
from config import cfg
from exceptions import NotFound, Redirect, PermanentRedirect, BasicAuth
from routing import auto_routing, add_apps, url4
from multidict import MultiDict, HeaderDict


class Request(object):
    charset = 'utf-8'
    encoding_errors = 'ignore'
    max_post_size = None  # максимальный размер post-данных
    _new_flashes = None
    _clear_flashes = False
    
    def __init__(self, environ):
        self.environ = environ
        self.path = environ['PATH_INFO'].decode(self.charset, self.encoding_errors)
    
    @cached_property
    def context(self):
        res = {'rq': self, 'url4': url4, 'cfg': cfg}
        for func in cfg.CONTEXT_PROCESSORS:
            res.update(func(self))
        return res

    @cached_property
    def method(self):
        return self.environ['REQUEST_METHOD'].upper()

    @cached_property
    def GET(self):
        return MultiDict((k.decode(self.charset, self.encoding_errors),
            v[-1].decode(self.charset, self.encoding_errors))
                for k, v in cgi.parse_qs(self.environ['QUERY_STRING']).iteritems())
        
    @cached_property
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
                if cfg.POST_MAX_MEMFILE:
                    part = stream.read(min(maxread, cfg.POST_MAX_MEMFILE))
                else:
                    part = stream.read()
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

    @cached_property
    def COOKIES(self):
        return SimpleCookie(self.environ.get('HTTP_COOKIE', ''))

    @cached_property
    def scheme(self):
        return self.environ.get('HTTP_X_SCHEME',
            self.environ.get('wsgi.url_scheme', 'http'))

    @cached_property
    def host(self):
        host = self.environ.get('HTTP_X_FORWARDED_HOST',
            self.environ.get('HTTP_HOST', None))
        if not host:
            host = self.environ.get('SERVER_NAME', '')
            port = self.environ.get('SERVER_PORT', '80')
            if self.scheme + port not in ('https443', 'http80'):
                host += ':' + port
        return host

    @cached_property
    def full_path(self):
        qs = self.environ.get('QUERY_STRING', '')
        return '%s?%s' % (self.path, qs) if qs else self.path

    @cached_property
    def url(self):
        '''Полный урл'''
        return '%s://%s%s' % (self.scheme, self.host, self.full_path)
    
    @cached_property
    def ip(self):
        '''
        Самый внешний ип
        '''
        return self.ip_list[-1]

    @cached_property
    def ip_list(self):
        '''
        Список ипов из заголовков проксей за исключением локальных
        '''
        ret = []
        ips = self.environ.get('HTTP_X_FORWARDED_FOR', self.environ.get(
            'HTTP_X_REAL_IP'))
        if ips:
            for ip in ips.split(','):
                ip = ip.strip()
                if ip.startswith(('10.', '192.168.')):
                    continue
                if ip.startswith('172.'):
                    try:
                        x = ip.split('.')[1]
                    except (ValueError, IndexError):
                        continue
                    if 15 < x < 31:
                        continue
                ret.append(ip)
        return ret or [self.environ.get('REMOTE_ADDR')]

    @cached_property
    def referer(self):
        return self.environ.get('HTTP_REFERER', '')
        
    @cached_property
    def user_agent(self):
        return self.environ.get('HTTP_USER_AGENT', '')
    
    @cached_property
    def basic_user(self):
        if cfg.BASIC_AUTH_SSL_ONLY and self.scheme != 'https':
            raise redirect('https://%s%s' % (self.host, self.full_path))
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
        
    @cached_property
    def flashes(self):
        ret = []
        if cfg.FLASH_COOKIE_NAME in self.COOKIES:
            self._clear_flashes = True
            ret = self.COOKIES[cfg.FLASH_COOKIE_NAME].value
            try:
                ret = marshal.loads(base64.urlsafe_b64decode(ret))
            except (EOFError, ValueError, TypeError):
                ret = []
        return ret

    def flash(self, msg, level='info'):
        if not isinstance(msg, unicode):
            msg = msg.decode(self.charset)
        self._new_flashes = self._new_flashes or []
        self._new_flashes.append((msg, level))


class Response(Exception):
    code = 200  # дефолтный код ответа
    charset = 'utf-8'  # дефолтная кодировка
    encoding_errors = 'ignore'
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

    def set_cookie(self, key, val, path='/', **kwargs):
        """
        Устанавливаем куку:
            *key        - (unicode) ключ
            *val        - (unicode) значение
            **path      - (unicode) uri, '/' - для действия на весь домен
            **expires   - (int) время жизни куки в секундах, дефолт - до закрытия браузера
            **domain    - (unicode) дефолт - текущий поддомен, '.site.name' - для всех поддоменов
        """
        key = key.encode(self.charset, self.encoding_errors)
        self.COOKIES[key] = val.encode(self.charset, self.encoding_errors)
        self.COOKIES[key]['path'] = path
        for k, v in kwargs.iteritems():
            self.COOKIES[key][k] = v
        return self
        
    def delete_cookie(self, key):
        return self.set_cookie(key, '', expires=-1)

    def wsgi(self):
        '''
        Возвращает переменные wsgi-ответа: status, headers и body
        '''
        status = '%i %s' % (self.code, HTTP_CODES.get(self.code, 'Unknown'))
        if isinstance(self.body, unicode):
            self.body = self.body.encode(self.charset, self.encoding_errors)
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
    def __init__(self, cfg_module='cfg'):
        '''
            *cfg_module - модуль конфигурации
        '''
        self.cfg_module = cfg_module


    def setup(self):
        '''
        Первый запуск
        '''
        def routing_queue(routing):
            list_obj_from_str(routing)
            def wrapper(rq):
                for func in routing:
                    try:
                        return func(rq)
                    except NotFound:
                        continue
                raise NotFound
            return wrapper
        
        cfg_module = obj_from_str(self.cfg_module)
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

        self.routing = obj_from_str(cfg.ROUTING)
        if isinstance(self.routing, tuple) or isinstance(self.routing, list):
            self.routing = routing_queue(self.routing)

        self.Request = Request

    def __call__(self, environ, start_response):
        try:
            rq = self.Request(environ)
        except AttributeError:
            # первый запуск
            self.setup()
            rq = self.Request(environ)
        try:
            for middleware in cfg.REQUEST_MIDDLEWARES:
                middleware(rq)
            res = self.routing(rq)
            if not isinstance(res, Response):
                res = Response(unicode(res), content_type='text/plain')
            for middleware in cfg.RESPONSE_MIDDLEWARES:
                middleware(rq, res)
        except Response, e:
            res = e
        except (Redirect, PermanentRedirect, BasicAuth), e:
            res = e.res
        except NotFound, e:
            if cfg.DEBUG:
                res = Response(make_traceback(rq.host),
                    code=404, content_type='text/plain')
            else:
                res = cfg.ERROR_PAGES[404](rq)
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


def redirect(url, permanent=False, **kwargs):
    '''
    Редирект
        *url        - url or urlname
    '''
    code = 301 if permanent else 302
    if not url.startswith(('/', 'http://', 'https://')):
        url = url4(url, **kwargs) or url
    return Response('', code=code, headers={'Location': url})


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
