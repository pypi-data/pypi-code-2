"""
SPARQL Endpoint
---------------

HTTP PUT and GET are both supported with identical parameters.

B{query}: the SPARQL query to execute

B{format}: the mime-type of the results. If not specified the type is inferred
from the I{HTTP Accept Header}. If an unsupported format is requested the
default is used. Supported formats are:

    - B{text/html} a human readable web page, the default value
    - B{application/sparql-results+json} JSON encoded results as defined
      in U{http://www.w3.org/TR/rdf-sparql-json-res/}

These values are defined in L{ordf.pylons.serialiser.sparql_serialisations}
"""
import logging

from ordf.onto.lib.base import BaseController, request, response, session, c
from ordf.onto.controllers.graph import GraphController
from ordf.graph import Graph, _Graph, ConjunctiveGraph
from ordf.namespace import RDF, RDFS
from ordf.term import URIRef

from pylons.controllers.util import abort
from pylons import config
from webhelpers.html.builder import literal

from traceback import format_exc

log = logging.getLogger(__name__)

serialisations = {
    "application/sparql-results+json": "json",
}

DEFAULT_QUERY = """\
SELECT DISTINCT ?thing ?type
WHERE {
    ?thing a ?type
}
LIMIT 10
"""

import re
_forbidden = re.compile(".*(INSERT|DELETE).*", re.IGNORECASE|re.MULTILINE)

class _Controller(BaseController):
    @staticmethod
    def _accept():
        if "format" in request.GET:
            content_type = request.GET["format"]
        else:
            content_type = request.accept.best_match(serialisations.keys() + ["text/html"])
        return content_type, serialisations.get(content_type, "html")

    def _get_query(self):
        query = request.POST.get("query", None)
        if query is None:
            query = request.GET.get("query", None)
        return query

    def _render(self, format):
        return self.render("sparql_%s.html" % format)

    def _render_graph(self):
        accept, format = GraphController._accept()
        if format != "html":
            ## special case for graph responses, don't use
            ## template, just serialise the graph. this happens
            ## with construct and describe queries
            response.content_type = str(accept)
            return c.graph.serialize(format=format)
        else:
            fresnel = GraphController._fresnel()
        for s in c.graph.distinct_subjects():
            if isinstance(s, URIRef):
                c.graph.add((s, RDF["type"], RDFS["Resource"]))
        c.stylesheets, content = fresnel.format(c.graph)
        c.content = literal(content)
        return self.render("sparql_%s.html" % format)

class FourStoreSparqlController(_Controller):
    def index(self):
        from py4s import FourStoreError

        c.stylesheets = []
        c.warnings = []
        c.bindings = []
        c.results = []
        c.boolean = False
        c.url = request.url

        store = self.handler.fourstore.store

        c.query = self._get_query()

        if c.query:
            if _forbidden.match(c.query.replace("\n", " ")):
                c.warnings = ["Operation Not Allowed"]
            else:
                cursor = store.cursor()
                try:
                    results = cursor.execute(c.query)
                    if isinstance(results, _Graph): 
                        c.graph = Graph(identifier=results.identifier)
                        c.graph += results.result
                        return self._render_graph()
                    else:
                        c.bindings = results.bindings
                        if results and not c.bindings:
                            c.boolean = True
                        c.results = list(results)
                except FourStoreError:
                    pass
                c.warnings = cursor.warnings
        else:
            c.query = DEFAULT_QUERY
        accept, format = self._accept()
        result = self._render(format)
        response.content_type = str(accept)
        return result

class RDFLibSparqlController(_Controller):
    def index(self):
        c.stylesheets = []
        c.warnings = []
        c.bindings = []
        c.results = []
        c.boolean = False
        c.url = request.url

        c.query = self._get_query()

        class BoundResult(object):
            def __init__(self, bindings, result):
                self.bindings = bindings
                self.result = result
            def __getitem__(self, k):
                if isinstance(k, int):
                    return self.result[k]
                return self.result[self.bindings.index(k)]

        if c.query:
            try:
                results = self.handler.rdflib.query(c.query)
            except:
                c.warnings = [format_exc()]
                results = None
            if results is None:
                pass ## some sort of error
            elif results.construct:
                c.graph = Graph(identifier=results.result.identifier)
                c.graph += results.result
                return self._render_graph()
            else:
                c.bindings = [x.lstrip("?") 
                                for x in results.selectionF 
                                    if x in results.allVariables]
                c.results = [BoundResult(c.bindings, x) for x in results]
        else:
            c.query = DEFAULT_QUERY
        content_type, format = self._accept()
        result = self._render(format)
        response.content_type = str(content_type)
        return result

if hasattr(BaseController.handler, "fourstore"):
    log.info("SPARQL endpoint using 4store")
    SparqlController = FourStoreSparqlController
elif hasattr(BaseController.handler, "rdflib"):
    log.info("SPARQL endpoint using rdflib")
    SparqlController = RDFLibSparqlController
