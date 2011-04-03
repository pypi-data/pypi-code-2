"""
RDF Proxy Service
-----------------

This controller is mainly intended for use by JavaScript applications that
are not able to connect to remote hosts and so cannot download RDF data from
them directly. As with L{ordf.pylons.graph} it takes the parameters
B{uri} and B{format} specifying the (remote) URI to fetch and the format
in which to return the results.

The controller will request the remote URI with I{application/rdf+xml} which
is the only official RDF serialisation, will parse it using L{ordf.graph.Graph}
and then serialise the results as requested.
"""
import logging
from cStringIO import StringIO

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons import config

from ordf.graph import Graph
from ordf.term import URIRef
from ordf.pylons import ControllerFactory
from ordf.pylons.serialiser import graph_format

log = logging.getLogger(__name__)

def ProxyControllerFactory(base, model):
    return ControllerFactory("ProxyController", _ProxyController, base, model)

class _ProxyController:
    def index(self):
        accept, format = graph_format(request)

        uri = request.GET.get("uri", None)
        if uri is None:
            c.message = "Missing GET parameter: uri"
            return self.render("proxy.html")

        graph = Graph(identifier=URIRef(uri))
        try:
            graph.parse(uri)
        except:
            response.content_type = "text/plain"
            return "Unable to parse or fetch %s" % (uri,)

        if format == "html":
            c.triples = graph.triples((None, None, None))
            data = self.render("graph.mako")
        else:
            data = graph.serialize(format=format)
            response.content_type = str(accept)
        return data
