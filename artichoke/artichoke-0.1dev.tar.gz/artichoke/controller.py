from webob import Request, Response
from webob.exc import HTTPTemporaryRedirect
from genshi.template import TemplateLoader
import inspect, pickle, base64

def expose(template = None,
           content_type = 'text/html'):

    if template == 'json':
        content_type = 'application/json'

    def decorate(f):
        f.exposed = True

        if not hasattr(f, 'artichoke'):
            f.artichoke = {}

        f.artichoke['template'] = template
        f.artichoke['content-type'] = content_type
        return f
    return decorate

class Controller(object):
    def __init__(self, template_path, helpers):
        self.loader = TemplateLoader([template_path])
        self.helpers = helpers
        self.templates = {}

    def render(self, template, params):
        try:
            tmpl = self.templates[template]
        except:
            tmpl = self.loader.load(template)
            self.templates[template] = tmpl

        stream = tmpl.generate(**params)
        return stream.render()

    def redirect(self, response, where):
        exc = HTTPTemporaryRedirect(location=where)
        try:
            exc.identity = response.identity
            if response.flash_obj:
                decoded_flash = pickle.dumps(response.flash_obj)
                exc.set_cookie('flash_obj', base64.b64encode(decoded_flash))
        except:
            pass
        raise exc

    @expose()
    def not_found(self, request, response, args, params):
        response.headers['Content-Type'] = 'text/html'
        response.status = 404
        return '''
<html>
   <head>
       <title>Page not Found</title>
   </head>
   <body>
       <h1>Page Not Found</h1>
       <div style="font-size:small">Artichoke Framework</div>
   </body>
</html>
'''

    def _dispatch(self, request):
        path = request.path_info.split('/')
        while path and not path[0]:
            path.pop(0)

        if not path:
            path = ['index']

        members = dict(inspect.getmembers(self))
        call = self

        if isinstance(call, Controller):
            while path[0:]:
                subpath = path[0]
                members = dict(inspect.getmembers(call))
                try:
                    call_candidate = members[subpath]
                    if isinstance(call_candidate, Controller) or \
                       (hasattr(call_candidate, 'exposed') and call_candidate.exposed):
                        call = call_candidate
                        path = path[1:]
                    else:
                        break
                except:
                    break

        if isinstance(call, Controller):
            if path:
                call = call.not_found
            else:
                call = call.index

        response = self.do_call(call, request, path[:])
        return response

    def do_call(self, call, request, path):
        response = Response(body="Artichoke Default Page", status=200)
        response.headerlist=[('Content-type', call.artichoke['content-type'])]
        self.inject_tools(request, response)

        if call.artichoke['template']:
            tmpl_context = {}
            tmpl_context['h'] = self.helpers
            tmpl_context['request'] = request
            tmpl_context['response'] = response
            tmpl_context.update(call(request, response, path, request.params))

            template = call.artichoke['template'] + '.html'
            response.body = self.render(template, tmpl_context)
        else:
            response.body = call(request, response, path, request.params)

        return response

    def inject_tools(self, request, response):
        def flash(msg, css_class='warning'):
            response.flash_obj = {'msg':msg, 'class':css_class}

        response.flash_obj = {}
        if request.cookies.get('flash_obj'):
            try:
                decoded_flash = request.cookies['flash_obj'].decode('base64')
                response.flash_obj = pickle.loads(decoded_flash)
            except Exception, e:
                print e
            response.delete_cookie('flash_obj')

        response.flash = flash