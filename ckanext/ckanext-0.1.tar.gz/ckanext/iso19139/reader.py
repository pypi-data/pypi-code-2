from amara.xslt.processor import processor
from amara.lib import inputsource

from ordf.namespace import register_ns, Namespace
register_ns("dcat", Namespace("http://www.w3.org/ns/dcat#"))

from ordf.graph import Graph
from ordf.namespace import DC, DCAT, RDF
from ordf.term import URIRef
try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO
import pkg_resources
import os


def iso2graph(isouri):
    P = processor()
    xslt = inputsource(pkg_resources.resource_stream(__name__, "iso19139_rdf.xsl"))
    P.append_transform(xslt)

    isoxml = inputsource(isouri)
    rdfxml = str(P.run(isoxml))

    g = Graph(identifier=URIRef(isouri)).parse(StringIO(rdfxml))
    s, _p, _o = g.one((None, RDF.type, DCAT.Catalog))
    g.add((s, DC.source, URIRef(isouri)))

    return g
