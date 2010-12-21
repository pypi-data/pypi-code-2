# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

from paste.httpexceptions import HTTPBadRequest

class WSGIApp(object):

    def routes_get(self):
        """Returns a list compatible with `selector.slurp`.
        """
        if hasattr(self, '_routes'):
            return [(key, self._routes[key]) for key in self._routes.keys()]

        # probably a filter app if routes have not been defined
        return []

    def routes_set(self, value):
        self._routes = value

    def routes_del(self):
        del self._routes
                
    routes = property(routes_get, routes_set, routes_del, routes_get.__doc__)

    def _check_arg(self, key, args):
        try:
            return args[key]
        except KeyError, e:
            raise HTTPBadRequest('The argument %s was not specified.' % key)

    def _check_content_size(self, env):
        try:
            return int(env['CONTENT_LENGTH'])
        except KeyError, ValueError:
            raise HTTPBadRequest('Content-Size header not defined or not an integer.')

    def _check_content_type(self, env):
        try:
            return env['CONTENT_TYPE']
        except KeyError, e:
            raise HTTPBadRequest('The Content-Type header was not defined.')
    
