"""
RDF Graph Controller - see L{ordf.pylons.graph}. 
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from pylons.controllers.util import abort
from pylons.decorators import jsonify
from openbiblio.lib import base
from openbiblio.lib.base import render, request, c, response
from openbiblio.lib.bibtex import Bibtex
from openbiblio import handler
from openbiblio.model.base import mapper
from openbiblio import model
from ordf.onto.controllers.graph import GraphController as _GraphController
from ordf.namespace import RDF
from ordf.graph import Graph
from ordf.term import URIRef

log = __import__("logging").getLogger(__name__)

construct_graph = u"""\
PREFIX dc: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
CONSTRUCT {
    %(agent)s a foaf:Agent .
    %(agent)s ?a_p ?a_o .
    ?work a bibo:Document .
    ?work dc:title ?title .
    ?work ?rel %(agent)s
} WHERE {
    ?anon owl:sameAs %(agent)s .
    ?anon ?a_p ?a_o .
    ?work a bibo:Document .
    ?work dc:title ?title .
    ?work ?rel ?anon
}    
"""

class GraphController(base.BaseController, _GraphController):
    def _get_or_infer_graph(self, uri):
        graph = handler.get(uri)
        if len(graph) == 0:
            q = construct_graph % { "agent" : uri.n3() }
            cg = handler.query(q)
            graph = Graph(identifier=uri)
            [graph.add(x) for x in cg.triples((None, None, None))]
            if len(graph) == 0:
                abort(404, "No such graph: %s" % uri)
            log.info("materialising %s" % uri.n3())
            handler.put(graph)
        return graph
    
    def rdf_serialise(self, content_type, format):
        uri = self._uri()
        if format in ("xml", "pretty-xml"): extension = ".rdf"
        else: extension = "." + format
        if not request.path.endswith(extension):
            response.headers["Location"] = str("%s%s" % (uri, extension))
            abort(303)
        g = self._get_or_infer_graph(uri)
        data = g.serialize()
        response.headers["Vary"] = "Accept"
        response.content_type = content_type
        response.headers["Content-Length"] = str(len(data))
        return g.serialize(format=format)

    def rdf_replace(self, content_type, format):
        uri = self._uri()
        user = c.author
        reason = request.GET.get("reason", "change via web")
        new = Graph(identifier=URIRef(uri))
        new.parse(StringIO(request.body), format=format)
        with handler.transaction():
            old = self.handler.get(uri)
            ### check authorisation here
            ctx = self.handler.context(user, reason)
            ctx.add(new)
            ctx.commit()
        log.info("change to %s from %s (%s)" % (uri, user, reason))
        return new.version()

    def rdf_append(self, content_type, format):
        uri = self._uri()
        user = c.author
        reason = request.GET.get("reason", "change via web")
        new = Graph(identifier=URIRef(uri))
        new.parse(StringIO(request.body), format=format)
        with handler.transaction():
            old = self.handler.get(uri)
            ### check authorisation here
            old += new ## assuming this will be quicker
            new = old ## to avoid confusing naming
            ctx = self.handler.context(user, reason)
            ctx.add(new)
            ctx.commit()
        log.info("change to %s from %s (%s)" % (uri, user, reason))
        return new.version()

    def rdf_remove(self, content_type, format):
        uri = self._uri()
        user = c.author
        reason = request.GET.get("reason", "change via web")
        new = Graph(identifier=URIRef(uri))
        new.parse(StringIO(request.body), format=format)
        with handler.transaction():
            old = self.handler.get(uri)
            ### check authorisation here
            ctx = self.handler.context(user, reason)
            ctx.remove(new)
            ctx.commit()
        log.info("change to %s from %s (%s)" % (uri, user, reason))
        return new.version()
        
    def html_view(self, *av):
        uri = self._uri()
        if uri.endswith(".html"):
            uri = URIRef(uri[:-5])
        c.graph = self._get_or_infer_graph(uri)
        ### introspect the type... could do something more clever here
        ### when we have potentially more types...
        implementations = mapper.implementations(c.graph, c.graph.identifier)
        ### kinda arbitrary... need some sort of model -> template mapping
        ### or something
        if len(implementations) == 0 or model.Entry not in implementations:
            data = self._render_graph()
        else:
            c.model = model.Entry(c.graph.identifier, graph=c.graph)
            if c.user != None:
                c.usercollections = model.Collection.get_by_user_uri(URIRef('http://bibliographica.org/account/'+c.user))
            data = render("view_bibo_book.html")
        if not request.path.endswith(".html"):
            response.headers["Content-Location"] = uri + ".html"
        response.headers["Content-Length"] = str(len(data))
        return data

    ### This only applies to entries so should probably not be in the
    ### generic graph view
    def bibtex_view(self, *av):
        uri = self._uri()
        if uri.endswith(".bibtex"):
            uri = URIRef(uri[:-7])
        graph = self._get_or_infer_graph(uri)
        b = Bibtex()
        b.load_from_graph(graph)
        data = b.to_bibtex()
        response.content_type = "text/x-bibtex"
        if not request.path.endswith(".bibtex"):
            response.headers['Content-Location'] = uri + ".bibtex"
        response.headers["Content-Length"] = str(len(data))
        return data

    @jsonify
    def json_view(self, *av):
        uri = self._uri()
        if uri.endswith(".json"):
            uri = URIRef(uri[:-5])
        graph = self._get_or_infer_graph(uri)

        ### introspect the type... could do something more clever here
        ### when we have potentially more types...
        implementations = mapper.implementations(graph, graph.identifier)
        if len(implementations) is None:
            abort(406) #### not acceptable

        ### maybe we can imagine a better way of chosing...
        from random import choice
        cls = choice(implementations)
        
        obj = cls(graph.identifier, graph=graph)
        response.content_type = "text/javascript"
        data = obj.to_dict()
#        from pprint import pprint
#        pprint (data)
        return data
