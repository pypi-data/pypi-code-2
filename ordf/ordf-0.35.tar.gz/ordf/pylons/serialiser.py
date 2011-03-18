"""
Content-Type Negotiation
------------------------

.. data:: graph_serialisations
.. autofunction:: graph_format
.. data:: sparql_serialisations
.. autofunction:: sparql_format

"""

graph_serialisations = {
    "application/rdf+xml" : "pretty-xml",
    "text/n3" : "n3",
    "text/plain" : "nt",
}
def graph_format(request):
    if "format" in request.GET:
        accept = request.GET["format"]
    else:
        accept = request.accept.best_match(graph_serialisations.keys() + ["text/html"])
    return accept, graph_serialisations.get(accept, "html")

sparql_serialisations = {
    "application/sparql-results+json": "json",
}
def sparql_format(request):
    if "format" in request.GET:
        accept = request.GET["format"]
    else:
        accept = request.accept.best_match(sparql_serialisations.keys() + ["text/html"])
    return accept, sparql_serialisations.get(accept, "html")

search_serialisations = {
    "application/javascript": "json"
}
def search_format(request):
    if "format" in request.GET:
        accept = request.GET["format"]
    else:
        accept = request.accept.best_match(search_serialisations.keys() + ["text/html"])
    return accept, search_serialisations.get(accept, "html")
