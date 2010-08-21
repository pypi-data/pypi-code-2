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

from pylons import request, response, session, tmpl_context as c
from pylons.controllers.util import abort
from pylons import config

from ordf.graph import _Graph
from ordf.namespace import bind_ns, namespaces

from ordf.pylons.serialiser import graph_format, sparql_format
from ordf.pylons import ControllerFactory

from traceback import format_exc

log = logging.getLogger(__name__)

DEFAULT_QUERY = """\
SELECT DISTINCT ?thing ?type
WHERE {
    ?thing a ?type
}
LIMIT 10
"""

import re
_forbidden = re.compile(".*(INSERT|DELETE).*", re.IGNORECASE|re.MULTILINE)

class _SparqlController:
    def _render(self, format):
        return self.render("sparql_%s.html" % format)
    def _get_query(self):
        query = request.POST.get("query", None)
        if query is None:
            query = request.GET.get("query", None)
        return query

class _FourStoreSparqlController(_SparqlController):
    def index(self):
        from py4s import FourStoreError

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
                        accept, format = graph_format(request)
                        if format != "html":
                            ## special case for graph responses, don't use
                            ## template, just serialise the graph. this happens
                            ## with construct and describe queries
                            bind_ns(results)
                            response.content_type = str(accept)
                            return results.serialize(format=format)
                        c.bindings = [0,1,2]
                        c.results = results.triples((None,None,None))
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
        accept, format = sparql_format(request)
        result = self._render(format)
        response.content_type = str(accept)
        return result

class _RDFLibSparqlController(_SparqlController):
    def index(self):
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
                g = results.result
                accept, format = graph_format(request)
                if format != "html":
                    ## special case for graph responses, don't use
                    ## template, just serialise the graph. this happens
                    ## with construct and describe queries
                    bind_ns(g)
                    response.content_type = str(accept)
                    return g.serialize(format=format)
                c.bindings = [0,1,2]
                c.results = g.triples((None,None,None))
            else:
                c.bindings = [x.lstrip("?") 
                                for x in results.selectionF 
                                    if x in results.allVariables]
                c.results = [BoundResult(c.bindings, x) for x in results]
        else:
            c.query = DEFAULT_QUERY
        accept, format = sparql_format(request)
        result = self._render(format)
        response.content_type = str(accept)
        return result

def SparqlControllerFactory(base, handler):
    if hasattr(handler, "fourstore"):
        log.info("SPARQL endpoint using 4store")
        return ControllerFactory("SparqlController", _FourStoreSparqlController, base, handler)
    elif hasattr(handler, "rdflib"):
        log.info("SPARQL endpoint using rdflib")
        return ControllerFactory("SparqlController", _RDFLibSparqlController, base, handler)
