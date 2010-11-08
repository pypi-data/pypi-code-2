import urllib2
from urlparse import urlparse
from datetime import datetime
from ordf.graph import ConjunctiveGraph, Graph
from ordf.collection import Collection
from ordf.namespace import Namespace, register_ns
register_ns("http", Namespace("http://www.w3.org/2006/http#"))
register_ns("meth", Namespace("http://www.w3.org/2008/http-methods#"))
register_ns("rdfg", Namespace("http://www.w3.org/2004/03/trix/rdfg-1/"))
from ordf.namespace import RDF, RDFS, DC, HTTP, METH, FOAF
from ordf.term import URIRef, BNode, Literal
from ckanrdf.command import Command

log = __import__("logging").getLogger("corscheck")

query = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX void: <http://rdfs.org/ns/void#>

SELECT DISTINCT ?dset, ?uri WHERE {
    <http://semantic.ckan.net/catalogue> dcat:record ?rec .
    ?rec dcat:dataset ?dset .
    { ?dset void:sparqlEndpoint ?uri } UNION
    { ?dset void:exampleResource ?uri }
}
"""

# http://www.voidspace.org.uk/python/articles/urllib2.shtml#id28
import socket
socket.setdefaulttimeout(30)

# http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

def record_headers(g, msg, hdict):
    for h in hdict:
        head = BNode()
        g.add((msg, HTTP["headers"], head))
        g.add((head, RDF["type"], HTTP["MessageHeader"]))
        g.add((head, HTTP["fieldName"], Literal(h)))
        g.add((head, HTTP["fieldValue"], Literal(hdict[h])))

class CorsCheck(Command):
    parser = Command.StandardParser(usage="%prog [options]")

    def command(self):
        log.info("starting up")
        store = self.handler.rdflib.store
        if hasattr(store, "sparql_query"):
            select = store.sparql_query
            store = store.clone()
        else:
            select = ConjunctiveGraph(store).query

        count = 0
        for dset, uri in select(query):
            count += 1
            log.info("Checking %s\n\t\t%s" % (dset, uri))

            request = HeadRequest(uri)

            ident = URIRef(dset + u"#cors")
            g = Graph(store, identifier=ident)
            g.add((ident, RDFS["comment"], Literal("CORS Checking HTTP HEAD Requests on void:sparqlEndpoint and void:exampleResource.")))
            g.add((ident, FOAF["primaryTopic"], dset))
            g.add((ident, DC["isPartOf"], URIRef("http://river.styx.org/ww/2010/10/corscheck")))

            conn = BNode()
            g.add((conn, RDF["type"], HTTP["Connection"]))
            g.add((conn, DC["date"], Literal(datetime.utcnow())))
            parsed = urlparse(uri)
            host, port = parsed.hostname, parsed.port
            if port is None:
                if parsed.scheme == "https:":
                    port = 443
                else:
                    port = 80
            g.add((conn, HTTP["connectionAuthority"],
                   Literal("%s:%s" % (host, port))))

            try:
                response = urllib2.urlopen(request)
            except urllib2.HTTPError, response:
                log.error("%s %s" % (uri, response))
            except urllib2.URLError, e:
                g.add((conn, RDFS["comment"], Literal(e.reason)))
                log.error("%s %s" % (uri, e))
                g.commit()
                continue
            
            req = BNode()
            g.add((conn, HTTP["requests"], req))
            g.add((req, RDF["type"], HTTP["Request"]))
            g.add((req, HTTP["methodName"], Literal("HEAD")))
            g.add((req, HTTP["mthd"], METH["HEAD"]))
            g.add((req, HTTP["requestURI"], uri))
            if request.headers:
                record_headers(g, req, request.headers)

            resp = BNode()
            g.add((req, HTTP["resp"], resp))
            g.add((resp, RDF["type"], HTTP["Response"]))
            g.add((resp, HTTP["statusCodeNumber"], Literal("%s" % response.getcode())))
            if response.headers:
                record_headers(g, resp, response.headers)

#            print g.serialize(format="n3")
#            break
            g.commit()

        log.info("done. checked %d resources" % count)

def corscheck():
    CorsCheck().command()
