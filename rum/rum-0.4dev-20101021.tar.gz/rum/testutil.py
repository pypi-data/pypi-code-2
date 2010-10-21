from urllib import urlencode, unquote
import simplejson
import turbojson
from webtest import TestApp
from webob.headerdict import HeaderDict

__all__ = ["RumTestApp"]

def make_poster(method):
    def poster(self, url, params='', headers=[], **kw):
        content_type = kw.get('type', 'application/x-www-form-urlencoded')
        if params:
            if 'urlencoded' in content_type:
                params = urlencode(params)
            elif 'json' in content_type:
                params = turbojson.encode(params)
        headers = HeaderDict(headers)
        headers['content-type'] = content_type
        _super = super(RumTestApp, self)
        return getattr(_super, method)(url, params, headers.items(), **kw)
    poster.func_name = method
    return poster

def prefix_adder(func):
    def entangled(self, url, *args, **kw):
        return func(self, self.prefix + url, *args, **kw)
    entangled.func_name = func.func_name
    return entangled

class RumTestApp(TestApp):

    def __init__(self, app, prefix=''):
        self.prefix = prefix
        TestApp.__init__(self, app)

    post = prefix_adder(make_poster('post'))
    put = prefix_adder(make_poster('put'))

    get = prefix_adder(TestApp.get)

    #XXX This one is broken in TestApp
    @prefix_adder
    def delete(self, url, headers=None, extra_environ=None,
               status=None, expect_errors=False):
        """
        Do a DELETE request.  Very like the ``.get()`` method.
        ``params`` are put in the body of the request.

        Returns a ``webob.Response`` object.
        """
        return self._gen_request('DELETE', url, params='', headers=headers,
                                 extra_environ=extra_environ,status=status,
                                 upload_files=None, expect_errors=expect_errors)

    @staticmethod
    def get_flash(resp, cookie_name='webflash'):
        return simplejson.loads(unquote(resp.cookies_set[cookie_name]))

