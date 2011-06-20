import os
import hashlib
from sha import sha
import time
import urllib
import logging

from webob import Request, Response
from simplejson import dumps
from shove import Shove
from paste.script import templates

from pydap.wsgi.file import supported
from pydap.handlers.lib import load_handlers


def make_middleware(app, global_conf, **kwargs):
    return JsonpMiddleware(app, global_conf=global_conf, **kwargs)


class JsonpMiddleware(object):
    def __init__(self, app, root, cache="cache.db", **kwargs):
        self.app = app
        self.root = root
        self.cache = Shove('sqlite:///%s' % cache, protocol=2)

        self.handlers = load_handlers()

    def __call__(self, environ, start_response):
        req = Request(environ)        

        jsonp = req.GET.get('callback')
        if req.path_info == '/jsonp/catalog':
            body = {}
            for root, dirs, filenames in os.walk(self.root):
                if not root.startswith('.'):
                    for filename in filenames:
                        filepath = os.path.abspath(os.path.join(root, filename))
                        url = filepath[len(self.root)+1:]
                        if not filename.startswith('.') and supported(filepath, self.handlers):
                            try:
                                mtime, md5 = self.cache[filepath]
                            except:
                                mtime, md5 = None, None
                            mtime_ = os.path.getmtime(filepath)
                            if mtime is None or mtime < mtime_:
                                mtime = mtime_
                                md5 = md5sum(filepath)
                                self.cache[filepath] = mtime, md5
                            body[url] = md5
            body = jsonp + '(' + dumps(body) + ')'
            etag = '"%s"' % sha(body).hexdigest()
            if etag in req.if_none_match:
                res = Response(status='304 Not Modified')
            else:
                res = Response(
                        body=body, 
                        content_type='text/javascript', 
                        charset='utf-8')
        elif req.path_info == '/jsonp/ping':
            body = jsonp + '(' + dumps('pong') + ')'
            res = Response(
                    body=body, 
                    content_type='text/javascript', 
                    cache_control='no-cache, no-store', 
                    charset='utf-8')
        else:
            # TODO: store latencies for benchmarking
            latencies = []
            for k, latency in req.str_cookies.items():
                if k.startswith('latency-to-'):
                    server = urllib.unquote_plus(k[11:])
                    latencies.append('%s %s ms' % (server, latency))
            latencies = '; '.join(latencies)

            res = req.get_response(self.app)

        return res(environ, start_response)


def md5sum(filepath, block_size=2**20):
    f = open(filepath)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    return md5.hexdigest()


class Template(templates.Template):

    egg_plugins = ['pydap']
    summary = 'Template for distributed pydap server installation.'
    _template_dir = 'template'
    use_cheetah = False
