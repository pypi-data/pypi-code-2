import docutils.core
import subprocess
from utils import import_path
from webob import Request, Response

import genshi
from genshi.template import MarkupTemplate

class Transformer(object):
    """abstract base class for transformer objects"""
    def __init__(self, content, content_type):
        self.content = content
        self.content_type = content_type

    def transform(self, request):
        """returns a tuple of (body, content-type)"""
        raise NotImplementedError

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.get_response(request)
        return response(environ, start_response)

    def get_response(self, request):
        if request.GET.get('format') == 'raw':
            return Response(content_type=self.content_type, body=self.content)
        content_type, body = self.transform(request)
        return Response(content_type=content_type, body=body)

class ContentTypeChanger(Transformer):
    def __init__(self, content, from_type, to_type):
        self.to_type = to_type
        Transformer.__init__(self, content, from_type)

    def transform(self, request):
        return (self.to_type, self.content)

class Graphviz(Transformer):
    content_types = { 'png': 'image/png',
                      'svg': 'image/svg+xml' }
    
    def __init__(self, content, content_type, format='png'):
        self.format=format
        Transformer.__init__(self, content, content_type)
    
    def transform(self, request):
        """create a Graphviz object"""
        _format = request.GET.get('format', self.format)
        assert _format in self.content_types, 'Unknown format: ' + _format
        process = subprocess.Popen(['dot', '-T' + _format],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE)
        image, _ = process.communicate(self.content)
        return (self.content_types[_format], image)

class RestructuredText(Transformer):
    settings = { 'report_level': 5 }

    def transform(self, request):
        """template: genshi(?) template to use (???)"""
        html = docutils.core.publish_string(self.content,
                                            writer_name='html',
                                            settings_overrides=self.settings)
        return ('text/html', html)


class GenshiTransformer(Transformer):

    def __init__(self, content, content_type, modules=()):
        """
        - modules : strings of modules
        """
        self.variables = {}
        for path in modules:
            module = import_path(path)
            name = path.rsplit('.')[-1]
            self.variables[name] = module
        Transformer.__init__(self, content, content_type)
        
    def transform(self, request):
        variables = dict(request=request)
        template = MarkupTemplate(self.content)
        stream = template.generate(**variables)
        return ('text/html', stream.render('html', doctype='html'))

