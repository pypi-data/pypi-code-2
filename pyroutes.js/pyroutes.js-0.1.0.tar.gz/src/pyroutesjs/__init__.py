import re, os.path

from simplejson import dumps

from webob import Request, Response
from paste.fileapp import DataApp

_argument_prog = re.compile('\{(.*?)\}|:\((.*)\)')

def _extract_route_information(route):
    routepath = route.routepath
    def replace(matchobj):
        if matchobj.group(1):
            return "%%(%s)s" % matchobj.group(1).split(':')[0]
        else:
            return "%%(%s)s" % matchobj.group(2)


    routepath = _argument_prog.sub(replace, routepath)
    return (
        routepath,
        [(arg[0].split(':')[0] if arg[0]!='' else arg[1]) for arg in _argument_prog.findall(route.routepath)]
    )

def render_pyroutes_js(mapper):
    matchlist_extraction = [
        _extract_route_information(route) for route in mapper.matchlist
    ]

    f = open(os.path.join(os.path.dirname(__file__), 'pyroutes.js'), "r")
    result = f.read().replace(
        '{MATCHLIST}',
        dumps(dict([ (route.name, _extract_route_information(route)) for route in mapper.matchlist ]), indent=4)
    )
    f.close()
    return result

class Middleware(object):
    def __init__(self, app, mapper, pyroutes_js_path='/js/pyroutes.js'):
        self.app = app
        self.pyroutes_js_path = pyroutes_js_path
        self.pyroutes_dataapp = DataApp(render_pyroutes_js(mapper))

    def __call__(self, environ, start_response):
        req = Request(environ)
        if req.path == self.pyroutes_js_path:
            resp = req.get_response(self.pyroutes_dataapp)
            return resp(environ, start_response)
        else:
            resp = req.get_response(self.app)
            return resp(environ, start_response)
