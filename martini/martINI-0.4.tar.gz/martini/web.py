"""
a view with webob + genshi for editing and viewing .ini files
"""
import os
import re

from genshi.template import TemplateLoader
from martini.config import ConfigMunger
from martini.utils import getbool
from martini.utils import getlist
from paste.httpexceptions import HTTPExceptionHandler
from paste.urlparser import StaticURLParser
from pkg_resources import resource_filename
from webob import Request, Response, exc

class MartiniWebView(object):

    ### class level variables
    defaults = { 'auto_reload': 'True',
                 'files': None,
                 'directories': None }

    def __init__(self, **kw):

        # set instance parameters from kw and defaults
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))
        self.auto_reload = getbool(self.auto_reload)

        # files
        self.files = getlist(self.files)
        if self.files:
            assert [ f for f in self.files if os.path.isabs(f) ]
            self.files = dict([(os.path.basename(f), f) 
                               for f in self.files])
        else:
            self.files = {}

        # directories
        self.directories = getlist(self.directories)
        if self.directories:
            assert [ d for d in self.directories if os.path.isabs(d) ]
            if len(self.directories) > 1 or self.files:
                # namespace directories
                self.directories = dict([(os.path.basename(d), d)
                                         for d in self.directories])
            else:
                # don't namespace a single directory
                self.directories = { '': self.directories[0] }
        else:
            self.directories = {}

        # have to have something to serve!
        assert self.files or self.directories

        # methods to respond to
        self.response_functions = { 'GET': self.get,
                                    'POST': self.post,
                                    }

        # template loader
        templates_dir = resource_filename(__name__, 'templates')
        self.loader = TemplateLoader(templates_dir,
                                     auto_reload=self.auto_reload)

        # fileserver
        self.fileserver = StaticURLParser(resource_filename(__name__, 'static'))

    def file(self, path):
        path = path.strip('/')
        if not path:
            return None
        f = self.files.get(path, None)
        if f is None:
            if path in self.directories:
                return self.directories[path]
            if '/' in path:
                path = path.split('/', 1)[-1]
                for d in self.directories.values():
                    filename = os.path.join(d, path)
                    if os.path.exists(filename):
                        return filename
        else:
            return f

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        request = Request(environ)

        if request.path_info.strip('/') and os.path.exists(os.path.join(resource_filename(__name__, 'static'), request.path_info.strip('/'))):
            return self.fileserver(environ, start_response)

        if request.path_info.endswith('/'):
            if request.path_info.strip('/'):
                raise exc.HTTPFound(location=request.path_info.rstrip('/'))
            else:
                if request.path_info != '/':
                    raise exc.HTTPFound(location='/')
        res = self.make_response(request)
        return res(environ, start_response)
                                
    def make_response(self, request):
        return self.response_functions.get(request.method, self.error)(request)

    def get_response(self, text, content_type='text/html'):
        """make an HTTP response from text"""
        res = Response(content_type=content_type, body=text)
        return res

    def get(self, request):
        """
        return response to a GET requst
        """

        # index of all resources
        if not request.path_info.strip('/'):
            template = self.loader.load('index.html')
            items = self.files.keys() + self.directories.keys()
            res = template.generate(request=request, items=items).render('html', doctype='html')
            return self.get_response(res)

        # get the file
        f = self.file(request.path_info)
        if not f:
            raise exc.HTTPNotFound()
        
        # index page of a directory
        if os.path.isdir(f):
            template = self.loader.load('index.html')
            items = os.listdir(f)
            res = template.generate(request=request, items=items).render('html', doctype='html')
            return self.get_response(res)

        # get configuration
        conf = ConfigMunger(f)

        # render the template
        template = self.loader.load('table.html')
        res = template.generate(request=request, sections=conf.dict()).render('html', doctype='html')
        # generate the response
        return self.get_response(res)

    def post(self, request):
        """
        return response to a POST request
        """

        if not request.path_info.strip('/'):
            raise exc.HTTPMethodNotAllowed()

        # get the file
        f = self.file(request.path_info)
        if not f:
            raise exc.HTTPNotFound()
        if os.path.isdir(f):
            raise exc.HTTPMethodNotAllowed()

        regex = '\[([^\]]+)\](.*)'

        conf = ConfigMunger(f)

        delete = request.POST.getall('delete')
        if delete:
            del request.POST['delete']

        for key, value in request.POST.items():
            value = ' '.join(value.strip().split())
            match = re.match(regex, key)
            section, option = match.groups()
            if option:
                conf.set(section, option, value)
            else:
                if value:
                    conf.move_section(section, value)
                else:
                    conf.add_section(section)
        
        for d in delete:
            match = re.match(regex, d)
            section, option = match.groups()
            if conf.has_section(section):
                if option:
                    conf.remove_option(section, option)
                else:
                    conf.remove_section(section)

        output = file(f, 'w')
        conf.write(output)

        return exc.HTTPSeeOther(location=request.path_info)

    def error(self, request):
        """deal with non-supported methods"""
        return exc.HTTPMethodNotAllowed("Only %r operations are allowed" % self.response_functions.keys())


### paste factory
        
def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    keystr = 'martini.'
    args = dict([(key.split(keystr, 1)[-1], value)
                 for key, value in app_conf.items()
                 if key.startswith(keystr) ])
    app = MartiniWebView(**args)
    return HTTPExceptionHandler(app)
