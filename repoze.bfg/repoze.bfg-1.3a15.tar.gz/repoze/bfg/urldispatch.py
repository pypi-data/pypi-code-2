import re
from urllib import unquote
from zope.interface import implements

from repoze.bfg.interfaces import IRoutesMapper
from repoze.bfg.interfaces import IRoute

from repoze.bfg.compat import all
from repoze.bfg.encode import url_quote
from repoze.bfg.exceptions import URLDecodeError
from repoze.bfg.traversal import traversal_path
from repoze.bfg.traversal import quote_path_segment


_marker = object()

class Route(object):
    implements(IRoute)
    def __init__(self, name, pattern, factory=None, predicates=(),
                 pregenerator=None):
        self.pattern = pattern
        self.path = pattern # indefinite b/w compat, not in interface
        self.match, self.generate = _compile_route(pattern)
        self.name = name
        self.factory = factory
        self.predicates = predicates
        self.pregenerator = pregenerator

class RoutesMapper(object):
    implements(IRoutesMapper)
    def __init__(self):
        self.routelist = []
        self.routes = {}

    def has_routes(self):
        return bool(self.routelist)

    def get_routes(self):
        return self.routelist

    def get_route(self, name):
        return self.routes.get(name)

    def connect(self, name, pattern, factory=None, predicates=(),
                pregenerator=None):
        if name in self.routes:
            oldroute = self.routes[name]
            self.routelist.remove(oldroute)
        route = Route(name, pattern, factory, predicates, pregenerator)
        self.routelist.append(route)
        self.routes[name] = route
        return route

    def generate(self, name, kw):
        return self.routes[name].generate(kw)

    def __call__(self, request):
        environ = request.environ
        try:
            # empty if mounted under a path in mod_wsgi, for example
            path = environ['PATH_INFO'] or '/' 
        except KeyError:
            path = '/'

        for route in self.routelist:
            match = route.match(path)
            if match is not None:
                preds = route.predicates
                info = {'match':match, 'route':route}
                if preds and not all((p(info, request) for p in preds)):
                    continue
                return info

        return {'route':None, 'match':None}

# stolen from bobo and modified
route_re = re.compile(r'(/:[a-zA-Z]\w*)')
def _compile_route(route):
    if not route.startswith('/'):
        route = '/' + route
    star = None
    if '*' in route:
        route, star = route.rsplit('*', 1)
    pat = route_re.split(route)
    pat.reverse()
    rpat = []
    gen = []
    prefix = pat.pop()
    if prefix:
        rpat.append(re.escape(prefix))
        gen.append(prefix)
    while pat:
        name = pat.pop()
        name = name[2:]
        gen.append('/%%(%s)s' % name)
        name = '/(?P<%s>[^/]+)' % name
        rpat.append(name)
        s = pat.pop()
        if s:
            rpat.append(re.escape(s))
            gen.append(s)

    if star:
        rpat.append('(?P<%s>.*?)' % star)
        gen.append('%%(%s)s' % star)

    pattern = ''.join(rpat) + '$'

    match = re.compile(pattern).match
    def matcher(path):
        m = match(path)
        if m is None:
            return m
        d = {}
        for k,v in m.groupdict().iteritems():
            if k is not None:
                if k == star:
                    d[k] = traversal_path(v)
                else:
                    encoded = unquote(v)
                    try:
                        d[k] = encoded.decode('utf-8')
                    except UnicodeDecodeError, e:
                        raise URLDecodeError(
                            e.encoding, e.object, e.start, e.end, e.reason
                            )
                        
                        
        return d
                    

    gen = ''.join(gen)
    def generator(dict):
        newdict = {}
        for k, v in dict.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if k == star and hasattr(v, '__iter__'):
                v = '/'.join([quote_path_segment(x) for x in v])
            elif k != star:
                try:
                    v = url_quote(v)
                except TypeError:
                    pass
            newdict[k] = v
        return gen % newdict

    return matcher, generator
