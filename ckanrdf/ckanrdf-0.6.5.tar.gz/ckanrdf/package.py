import ckanclient
import urllib
from pprint import pformat

from ordf.graph import Graph
from ordf.namespace import DC, DCAT, FOAF, LICENSES, OWL, RDF, RDFS, REV, SCOVO, UUID, VOID, XSD, OPMV
from ordf.term import URIRef as _URIRef, Literal as _Literal, BNode
from ordf.vocab.opmv import Agent, Process

log = __import__("logging").getLogger("ckanrdf.package")

#
# CKAN gives us data HTML escaped. We don't want that
# when storing with RDFLib. So this function and the
# two wrappers for Literal and URIRef de-escape the
# characters
#
from htmlentitydefs import name2codepoint
import re
_htmle_re = re.compile('&(%s);' % '|'.join(name2codepoint))
def htmlentitydecode(s):
    try:
        return _htmle_re.sub(lambda m: unichr(name2codepoint[m.group(1)]), s)
    except UnicodeError:
        return s
def Literal(x, *av, **kw):
    if isinstance(x, basestring):
        return _Literal(htmlentitydecode(x.strip()), *av, **kw)
    return _Literal(x, *av, **kw)

def URIRef(x, *av, **kw):
    clean = htmlentitydecode(x.strip())
    p,q = urllib.splitquery(clean)
    if q:
        uri = p + "?" + q.replace(":", "%3a"
                            ).replace("/", "%2f"
                            )
    else:
        uri = p
    return _URIRef(uri, *av, **kw)

class Tag(object):
    def __init__(self, config):
        self.config = config
    def tag_base(self):
        return self.config.get("ckan_tag_base",
                               self.ckan_base() + "tag/")
    def tag_uri(self, tagname):
        return URIRef(self.tag_base() + tagname)

class Package(object):
    def __init__(self, config):
        self.config = config
        self.tags = Tag(config)

    def api_base(self):
        return self.config.get("ckan_api_base",
                               self.ckan_base() + "api")

    def ckan_base(self):
        return self.config.get("ckan_base", "http://ckan.net/")

    def pkg_base(self):
        return self.config.get("ckan_pkg_base",
                               self.ckan_base() + "package/")
    def pkg_uri(self, data):
        if "ckan_url" in data and data["ckan_url"]:
            uri = data["ckan_url"]
            del data["ckan_url"]
            return URIRef(uri)
        return URIRef(self.pkg_base() + data["name"])

    def rdf_base(self):
        return self.config.get("rdf_base", "http://semantic.ckan.net/")
    def rdf_cat_base(self):
        return self.config.get("rdf_cat_base", self.rdf_base() + "catalogue")
    def rdf_pkg_base(self):
        return self.config.get("rdf_pkg_base", self.rdf_base() + "package/")
    def rdf_pkg_uri(self, data):
        return URIRef(self.rdf_pkg_base() + data["name"])
    def sparql_endpoint(self):
        return self.config.get("sparql_endpoint", "http://semantic.ckan.net/sparql")

    def build_catalogue(self, packages, store="IOMemory"):
        rdf_uri = URIRef(self.rdf_cat_base())
        catalogue = Graph(store, identifier=rdf_uri)
        catalogue.remove((None, None, None))
        catalogue.add((rdf_uri, RDF["type"], DCAT["Catalog"]))
        catalogue.add((rdf_uri, RDF["type"], VOID["Dataset"]))
        catalogue.add((rdf_uri, DC.publisher,
                       URIRef(self.config.get("rdf_publisher", "http://ckan.net/"))))
        catalogue.add((rdf_uri, VOID["sparqlEndpoint"], URIRef(self.sparql_endpoint())))

        for pkg in packages:
            catalogue.add((rdf_uri, DCAT.record, self.rdf_pkg_uri(pkg)))

        return catalogue

    def describe(self, data, store="IOMemory"):
        log.info("Describing %(name)s" % data)
        uri = self.pkg_uri(data)
        rdf_uri = self.rdf_pkg_uri(data)
        
        fix = Graph(store, identifier=self.rdf_pkg_base() + data["name"][0] + "/" + data["name"][1] + "/" + data["name"])
        fix.remove((None, None, None))
        store.commit()


        rec = Graph(store, identifier=rdf_uri)
        rec.remove((None, None, None))

        rec.add((rdf_uri, RDF["type"], DCAT["CatalogRecord"]))
        rec.add((rdf_uri, DC["publisher"],
                    URIRef(self.config.get("rdf_publisher", "http://ckan.net/"))))
        rec.add((rdf_uri, DCAT["dataset"], uri))
        rec.add((rdf_uri, FOAF["isPrimaryTopicOf"], URIRef(rdf_uri + ".rdf")))
        rec.add((rdf_uri, FOAF["isPrimaryTopicOf"], URIRef(rdf_uri + ".n3")))
        rec.add((rdf_uri, FOAF["isPrimaryTopicOf"], URIRef(rdf_uri + ".nt")))
        rec.add((URIRef(rdf_uri + ".rdf"), FOAF["primaryTopic"], rdf_uri))
        rec.add((URIRef(rdf_uri + ".n3"), FOAF["primaryTopic"], rdf_uri))
        rec.add((URIRef(rdf_uri + ".nt"), FOAF["primaryTopic"], rdf_uri))

        rec.add((uri, RDF["type"], DCAT["Dataset"]))
        rec.add((uri, FOAF["page"], URIRef(rdf_uri + ".rdf")))
        rec.add((uri, FOAF["page"], URIRef(rdf_uri + ".n3")))
        rec.add((uri, FOAF["page"], URIRef(rdf_uri + ".nt")))
        rec.add((URIRef(rdf_uri + ".rdf"), FOAF["topic"], uri))
        rec.add((URIRef(rdf_uri + ".n3"), FOAF["topic"], uri))
        rec.add((URIRef(rdf_uri + ".nt"), FOAF["topic"], uri))
        rec.add((uri, OWL["sameAs"], UUID[data["id"]]))
        rec.add((uri, DC["identifier"], Literal(data["name"])))
        del data["id"]

        if data["url"] is not None and data["url"].strip():
            rec.add((uri, FOAF["homepage"], URIRef(data["url"].strip())))
        del data["url"]

        if data["title"] is not None:
            rec.add((rdf_uri, RDFS["label"], Literal("Record: %s" % data["title"])))
            rec.add((rdf_uri, DC["title"], Literal("Record: %s" % data["title"])))
            rec.add((uri, RDFS["label"], Literal(data["title"])))
            rec.add((uri, DC["title"], Literal(data["title"])))
        else:
            rec.add((rdf_uri, RDFS["label"], Literal("Record: %s" % data["name"])))
            rec.add((uri, RDFS["label"], Literal(data["name"])))
        del data["title"]
        del data["name"]

        if data["notes"] is not None:
            rec.add((uri, DC["description"], Literal(data["notes"])))
        del data["notes"]

        if data["license_id"] is not None:
            rec.add((uri, DC["rights"], LICENSES[data["license_id"]]))
        del data["license"]
        del data["license_id"]

        author = BNode()
        if data["author"] or data["author_email"]:
            rec.add((uri,DC.creator, author))
        if data["author"]:
            rec.add((author,FOAF.name, Literal(data["author"])))
        if data["author_email"]:
            rec.add((author,FOAF.mbox, URIRef("mailto:" + data["author_email"])))
        del data["author"]
        del data["author_email"]

        maintainer = BNode()
        if data["maintainer"] or data["maintainer_email"]:
            rec.add((uri,DC.contributor, maintainer))
        if data["maintainer"]:
            rec.add((maintainer,FOAF.name, Literal(data["maintainer"])))
        if data["maintainer_email"]:
            rec.add((maintainer,FOAF.mbox, URIRef("mailto:" + data["maintainer_email"])))
        del data["maintainer"]
        del data["maintainer_email"]

        for tag in data["tags"]:
            rec.add((uri, DCAT["keyword"], Literal(tag)))
        del data["tags"]

        if data["ratings_average"] is not None:
            rec.add((uri,REV.rating,
                     Literal(data["ratings_average"], datatype=XSD.float)))
        # can't useREV.totalVotes since that implies being a Review
        # ask Mr. Ayers
        #if data["ratings_count"] is not None:
        #    g.add((uri,REV.totalVotes,
        #           Literal(data["ratings_count"], datatype=XSD.integer)))
        del data["ratings_average"]
        del data["ratings_count"]

        for rdata in data["resources"]:
            self._process_resources(rec, uri, rdata)
        del data["download_url"]
        del data["resources"]

        for k,v in data["extras"].items():
            self._process_extra(rec, uri, k, v)
        del data["extras"]

        for rdata in data["relationships"]:
            self._process_relationship(rec, uri, rdata)
        del data["relationships"]

        ## TODO handle groups and version
        del data["groups"]
        del data["version"]

        ## TODO something with these?
        del data["revision_id"]
        del data["state"]

        if data:
            log.info("Unhandled information in %s:\n%s" % (uri, pformat(data)))

        agent = Agent()
        agent.nick(self.config.get("ckanrdf_user"))
        proc = Process(identifier=URIRef(rec.identifier + "#" + BNode()))
        proc.agent(agent)
        proc.use(self.api_base())
        proc.use(uri)
        proc.result(rec)

        for ext in (".rdf", ".n3", ".nt"):
            doc = URIRef(rdf_uri + ext)
            rec.add((doc, RDF["type"], OPMV["Artifact"]))
            rec.add((doc, OPMV["wasGeneratedBy"], proc.identifier))

        return rec

    def _process_resources(self, rec, uri, rdata):
        if rdata["format"] == "api/sparql":
            ## RDF datasets with SPARQL endpoints are marked so by LOD
            rec.add((uri, RDF["type"], VOID["Dataset"]))
            rec.add((uri, VOID["sparqlEndpoint"], URIRef(rdata["url"])))
        elif rdata["format"] == "meta/rdf-schema":
            rec.add((uri, RDF["type"], VOID["Dataset"]))
            rec.add((uri, VOID["vocabulary"], URIRef("http://www.w3.org/2000/01/rdf-schema#")))
        elif rdata["format"] == "meta/void":
            rec.add((uri, RDF["type"], VOID["Dataset"]))
            rec.add((uri, VOID["vocabulary"], VOID[""]))
        elif rdata["format"] == "meta/owl":
            rec.add((uri, RDF["type"], VOID["Dataset"]))
            rec.add((uri, VOID["vocabulary"], OWL[""]))
        elif rdata["format"] in ("application/x-ntriples", "application/x-nquads", "application/rdf+xml", "text/n3", "text/turtle"):
            rec.add((uri, RDF["type"], VOID["Dataset"]))
            dump = URIRef(rdata["url"])
            rec.add((uri, VOID["dataDump"], dump))
            format = self.get_format(rdata["format"])
            rec.add((dump, DC["format"], format.identifier))
            rec += format
        elif rdata["format"] in ("example/rdf+xml", "example/n3", "example/ntriples", "example/turtle", "example/rdfa"):
            example = URIRef(rdata["url"])
            rec.add((uri, VOID["exampleResource"], example))
            format = self.get_format(rdata["format"])
            rec.add((example, DC["format"], format.identifier))
            rec += format
            if rdata["description"]:
                rec.add((example, RDFS["label"], Literal(rdata["description"])))
        else:
            resource = BNode()
            rec.add((uri, DCAT["distribution"], resource))
            rec.add((resource, RDF["type"], DCAT["Distribution"]))
            rec.add((resource, DCAT["accessURL"], URIRef(rdata["url"])))
            if rdata["format"]:
                format = self.get_format(rdata["format"])
                rec.add((resource, DC["format"], format.identifier))
                rec += format
            if rdata["description"]:
                rec.add((resource, RDFS["label"], Literal(rdata["description"])))

    def get_format(self, format):
        g = Graph()
        format = format.lower()
        format_map = {
            "application/rdf+xml": ("application/rdf+xml", "RDF/XML"),
            "example/rdf+xml": ("application/rdf+xml", "RDF/XML"),
            "text/turtle": ("text/turtle", "RDF/Turtle"),
            "example/turtle": ("text/turtle", "RDF/Turtle"),
            "text/n3": ("text/n3", "RDF/N3"),
            "example/n3": ("text/n3", "RDF/N3"),
            "application/x-ntriples": ("application/x-ntriples", "RDF/NTriples"),
            "example/ntriples": ("application/x-ntriples", "RDF/NTriples"),
            "application/x-nquads": ("application/x-nquads", "RDF/NQuads"),
            "example/nquads": ("application/x-nquads", "RDF/NQuads"),
            "rdfa": ("application/xhtml+xml", "RDFa"),
            "example/rdfa": ("application/xhtml+xml", "RDFa"),
            "meta/sitemap": ("application/xml", "Semantic Sitemap"),

            "application/zip": ("application/zip", "ZIP"),
            "zip": ("application/zip", "ZIP"),
            "application/atom+xml": ("application/atom+xml", "ATOM"),
            "application/xml+atom": ("application/atom+xml", "ATOM"),
            "atom": ("application/atom+xml", "ATOM"),
            "text/plain": ("text/plain", "Text"),
            "text/ascii": ("text/plain", "Text"),
            "application/xhtml": ("application/xhtml", "HTML"),
            "application/xhtml+xml": ("application/xhtml+xml", "HTML"),
            "text/html": ("text/html", "HTML"),
            "html": ("text/html", "HTML"),
            "application/x-javascript": ("application/x-javascript", "JavaScript/JSON"),
            "json": ("application/x-javascript", "JSON"),
            "pdf": ("application/pdf", "PDF"),
            "pdf": ("application/pdf", "PDF"),
            "text/tab-separated-values": ("text/tab-separated-values", "TSV"),
            "tsv": ("text/tab-separated-values", "TSV"),
            "text/csv": ("text/csv", "CSV"),
            "csv": ("text/csv", "CSV"),
            "application/vnd.ms-excel": ("application/vnd.ms-excel", "XLS"),
            "xls": ("application/vnd.ms-excel", "XLS"),
            "application/marc": ("application/marc", "MARC"),
            "marc": ("application/marc", "MARC"),
            "application/vnd.google-earth.kml+xml": ("application/vnd.google-earth.kml+xml", "KML"),
            "kml": ("application/vnd.google-earth.kml+xml", "KML"),
            "application/vnd.google-earth.kmz": ("application/vnd.google-earth.kmz", "KMZ"),
            "kmz": ("application/vnd.google-earth.kmz", "KMZ"),
            }

        if format in format_map:
            value, label = format_map.get(format)
            g.add((g.identifier, RDF["type"], DC["IMT"]))
            g.add((g.identifier, RDF["value"], Literal(value)))
            g.add((g.identifier, RDFS["label"], Literal(label)))
        else:
            log.warning("Unknown format: %s" % format)
            g.add((g.identifier, RDFS["label"], Literal(format)))
        return g

    def _process_extra(self, rec, uri, key, value):
        if isinstance(value, basestring):
            value = value.strip()
            lval = value.lower()
            if "unknown" in lval or "not specified" in lval:
                value = None
        if value is None or value == '':
                return

        if key.startswith("links:"):
            self._process_linkset(rec, uri, key, value)
        elif key == "triples":
            rec.add((uri, RDF["type"], VOID["Dataset"]))
            rec.add((uri, VOID["triples"], Literal(int(value)))) 
        elif key == "shortname":
            rec.add((uri, RDFS["label"], Literal(value)))
        elif key == "license_link":
            rec.add((uri, DC["rights"], URIRef(value)))
        elif key == "date_created":
            rec.add((uri, DC["created"], Literal(value)))
        elif key == "date_published":
            rec.add((uri, DC["available"], Literal(value)))
        elif key == "date_listed":
            rec.add((uri, DC["available"], Literal(value)))
        elif key == "update_frequency":
            freq = BNode()
            rec.add((uri, DC["accrualPeriodicity"], freq))
            rec.add((freq, RDF["value"], Literal(value)))
            rec.add((freq, RDFS["label"], Literal(value)))
        elif key == "unique_id":
            rec.add((uri, DC["identifier"], Literal(value)))
        elif key == "geospatial_coverage":
            rec.add((uri, DC["spatial"], Literal(value)))
        elif key == "temporal_coverage":
            rec.add((uri, DC["temporal"], Literal(value)))
        elif key == "granularity":
            rec.add((uri, DCAT["granularity"], Literal(value)))
        else:
            log.warning("Unknown extra in %s: %s = %s" % (uri.rsplit("/", 1)[-1], key, value))

    def _process_relationship(self, rec, uri, rdata):
        if rdata["type"] == "linked_from":
            pass
        else:
            log.warning("Unknown relationship in %s: %s" % (uri.rsplit("/", 1)[-1], rdata))

    def _process_linkset(self, rec, uri, key, value):
        _unused, target = key.split(":")
        target = self.pkg_uri({ "name" : target })
        linkset = BNode()
        rec.add((uri, VOID["subset"], linkset))
        rec.add((linkset, RDF["type"], VOID["Linkset"]))
        rec.add((linkset, VOID["subjectTarget"], uri))
        rec.add((linkset, VOID["objectTarget"], target))
        count = BNode()
        rec.add((linkset, VOID["triples"], Literal(int(value))))
