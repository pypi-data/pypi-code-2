"""
URI Dereferencing
-----------------

Read and write individual RDF Graphs.

All parameters may be included as part of the request, using the convention
of HTTP GET parameters. This is true also of HTTP PUT operations. Some 
parameters, if they are not included in this way are inferred as described
below.

Two parameters are relevant for read (HTTP GET) operations on the datastore:

:uri: URI of the graph requested. If not specified the request URI is
    used. In this way *dereferencing* is supported. If the graph controller is
    used with a wildcard route, requesting *http://example.org/resource/MyGraph*
    will cause that graph (assuming it exists in the datastore) to be returned.

:format: mime-type of the results. If not specified, *content auto-negotiation*
    is used, by looking at the *Accept HTTP Header*. If an unsupported type is 
    requested the default is used. Supported values are:

    - *text/html* a human readable web page, the default value
    - *application/rdf+xml* the standard RDF interchange serialisation
    - *text/n3* an expressive machine and human readable serialisation
    - *text/plain* aka *ntriples*, easy to parse but not very readable

These values are defined in L{ordf.pylons.serialiser.graph_serialisations}.

For example, assuming the presence of the graph named I{http://example.org/test} and
supposing that I{example.org} has the IP address I{127.0.0.1}, the following 
examples are equivalent:

    - I{curl -H "Accept: text/n3" http://example.org/test}
    - I{curl http://example.org/test?format=text/n3}
    - I{curl -H "Accept: text/n3" http://localhost/graph?uri=http://example.org/test}
    - I{curl http://localhost/graph?uri=http://example.org/test&format=text/n3}

For write (HTTP PUT) operations an additional parameter is supported, namely
B{reason} which is interpreted as the comment or description of any changes
made and stored in a L{ordf.changeset.ChangeSet} object. The returned value
is the URI of the ChangeSet that has been created.
"""
__all__ = ["GraphControllerFactory"]

import logging
from cStringIO import StringIO

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons import config
from traceback import format_exc

from ordf.changeset import ChangeSet
from ordf.graph import Graph
from ordf.term import URIRef
from ordf.pylons import ControllerFactory
from ordf.pylons.serialiser import graph_format

log = logging.getLogger(__name__)

def get_user(request):
    user = []
    if request.remote_user:
        user.append(request.remote_user)
    if request.remote_addr:
        user.append(request.remote_addr)
    return " ".join(user)
def get_reason(request):
    return request.GET.get("reason", "change via web")

class _GraphController:

    def index(self):
        '''An example index method. In general you will want to override this
        in an inheriting class.
        '''
        try:
            accept, format = graph_format(request)
        except:
            log.error(format_exc())
            abort(406, "Not Acceptable Here")
        uri = self._uri()

        if request.method == "PUT":
            ## TODO: authentication
            data = self._save(uri, format)
        else:
            graph = self._graph(uri)
            if len(graph) == 0:
                abort(404, "No such graph")

            if format == "html":
                c.graph = graph
                data = self._render()
            else:
                data = graph.serialize(format=format)
                response.content_type = str(accept)
        return data

    def add(self):
        return self._render()

    def _render(self):
        return self.render("graph")

    def _uri(self):
        if "uri" in request.GET:
            uri = request.GET["uri"]
        else:
            uri = "%s://%s%s" % (request.scheme, request.host, request.path)
        return uri

    def _graph(self, uri):
        return self.handler.get(uri)

    def _save(self, uri, format):
        accept, format = graph_format(request)
        new = Graph(identifier=URIRef(uri))
        if format == "pretty-xml": parse_format = "xml"
        else: parse_format = format
        new.parse(StringIO(request.body), format=parse_format)
        user, reason = get_user(request), get_reason(request)
        ctx = self.handler.context(user, reason)
        ctx.add(new)
        ctx.commit()
        log.info("change to %s from %s (%s)" % (uri, user, reason))
        return new.version()


def GraphControllerFactory(base, handler):
    """
    Return a I{GraphController} class, handling inheritance from I{base.BaseController}
    that will have the I{handler} instance available as a class variable.
    """
    return ControllerFactory("GraphController", _GraphController, base, handler)

