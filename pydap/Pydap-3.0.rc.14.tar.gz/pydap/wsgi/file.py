"""
A simple file-based Opendap server.

Serves files from a root directory, handling those recognized by installed
handlers.

"""

import re
import os
from urllib import unquote
import time

from paste.request import construct_url
from paste.httpexceptions import HTTPNotFound
from paste.fileapp import FileApp

from pydap.handlers.lib import get_handler, load_handlers
from pydap.lib import __version__
from pydap.exceptions import ExtensionNotSupportedError
from pydap.util.template import FileLoader, GenshiRenderer


class FileServer(object):
    def __init__(self, root, templates='templates', catalog='catalog.xml', **config):
        self.root = root.replace('/', os.path.sep)
        self.catalog = catalog
        self.config = config

        loader = FileLoader(templates)
        self.renderer = GenshiRenderer(
                options={}, loader=loader)

        self.handlers = load_handlers()

    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        filepath = os.path.abspath(os.path.normpath(os.path.join(
                self.root,
                path_info.lstrip('/').replace('/', os.path.sep))))
        basename, extension = os.path.splitext(filepath)
        assert filepath.startswith(self.root)  # check for ".." exploit

        # try to set our renderer as the default, it none exists
        environ.setdefault('pydap.renderer', self.renderer) 

        if path_info.endswith('/'):
            return self.index(environ, start_response,
                    'index.html', 'text/html')
        elif os.path.exists(filepath):
            return FileApp(filepath)(environ, start_response)
        elif os.path.exists(basename):
            # Update environ with configuration keys (environ wins in case of conflict).
            for k in self.config:
                environ.setdefault(k, self.config[k])
            handler = get_handler(basename, self.handlers)
            return handler(environ, start_response)
        elif path_info.endswith('/%s' % self.catalog):
            environ['PATH_INFO'] = path_info[:path_info.rfind('/')]
            return self.index(environ, start_response,
                    'catalog.xml', 'text/xml')
        else:
            return HTTPNotFound()(environ, start_response)

    def index(self, environ, start_response, template_name, content_type):
        # Return directory listing.
        path_info = environ.get('PATH_INFO', '')
        directory = os.path.abspath(os.path.normpath(os.path.join(
                self.root,
                path_info.lstrip('/').replace('/', os.path.sep))))
        dirs = []
        files = []
        for name in os.listdir(directory):
            path = os.path.normpath(os.path.join(directory, name))
            if os.path.isdir(path) and not name.startswith('.'):
                dirs.append(name)
            elif os.path.isfile(path) and not name.startswith('.'):
                statinfo = os.stat(path)
                file = {'name': name,
                        'size': format_size(statinfo[6]),
                        'modified': time.localtime(statinfo[8]),
                        'supported': False}
                try:
                    get_handler(path, self.handlers)
                    file['supported'] = True
                except ExtensionNotSupportedError:
                    pass
                files.append(file)
        # Sort naturally using Ned Batchelder's algorithm.
        dirs.sort(key=alphanum_key)
        files.sort(key=lambda l: alphanum_key(l['name']))

        # Base URL.
        location = construct_url(environ, with_query_string=False)
        base = construct_url(environ, with_query_string=False, with_path_info=False)

        context = {
                'environ': environ,
                'root': construct_url(environ, with_query_string=False, with_path_info=False).rstrip('/'),
                'base': base,
                'location': location,
                'title': 'Index of %s' % unquote(environ.get('PATH_INFO') or '/'),
                'dirs' : dirs,
                'files': files,
                'catalog': self.catalog,
                'version': '.'.join(str(d) for d in __version__)
        }
        template = environ['pydap.renderer'].loader(template_name)
        output = environ['pydap.renderer'].render(template, context, output_format=content_type)
        headers = [('Content-type', content_type)]
        start_response("200 OK", headers)
        return [output]


# http://svn.colorstudy.com/home/ianb/ImageIndex/indexer.py
def format_size(size):
    if not size:
        return 'empty'
    if size > 1024:
        size = size / 1024.
        if size > 1024:
            size = size / 1024.
            return '%.1i MB' % size
        return '%.1f KB' % size
    return '%i bytes' % size


def alphanum_key(s):
    """
    Turn a string into a list of string and number chunks.

        >>> alphanum_key("z23a")
        ['z', 23, 'a']

    From http://nedbatchelder.com/blog/200712.html#e20071211T054956

    """
    def tryint(s):
        try:
            return int(s)
        except:
            return s
    return [tryint(c) for c in re.split('([0-9]+)', s)]


def make_app(global_conf, root, templates, **kwargs):
    return FileServer(root, templates=templates, **kwargs)
