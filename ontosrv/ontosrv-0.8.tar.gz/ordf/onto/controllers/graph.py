import logging

from ordf.onto.lib.base import BaseController, request, response, session, c
from ordf.graph import Graph
from ordf.namespace import RDF, RDFS, ORDF
from ordf.term import URIRef
from ordf.vocab.fresnel import Fresnel
from pylons.controllers.util import abort, redirect
from pylons.decorators.cache import beaker_cache, create_cache_key
from pylons import cache
from webhelpers.html.builder import literal
from pylons import config
from cStringIO import StringIO

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET

log = logging.getLogger(__name__)

serialisations = {
    "application/rdf+xml" : "xml",
    "text/n3" : "n3",
    "text/plain" : "nt",
}

class GraphController(BaseController):
#    @staticmethod
    def _accept(self, uri):
        if "format" in request.GET:
            content_type = request.GET["format"]
            format = serialisations.get(content_type, "html")
        elif hasattr(self, "_extension"):
            ## kludge
            if self._extension == "rdf": content_type = "application/rdf+xml"
            elif self._extension == "n3": content_type = "text/n3"
            elif self._extension == "nt": content_type = "text/plain"
            else: content_type = "text/html"
            format = serialisations.get(content_type, "html")
        else:
            content_type = request.accept.best_match(serialisations.keys() + ["text/html"])
            if content_type == "text/html":
                response.headers["Content-Location"] = str("%s.html" % uri)
            format = serialisations.get(content_type, "html")
            if format == "xml":
                format = "rdf"
            if format in ("rdf", "n3", "ttl", "nt"):
                response.headers["Location"] = str("%s.%s" % (uri, format))
                abort(303)
        return content_type, format

    def _content_type(self):
        if "format" in request.GET:
            content_type = request.GET["format"]
        else:
            content_type = request.content_type
        return content_type, serialisations.get(content_type, "xml")

    def _uri(self):
        if "uri" in request.GET:
            uri = request.GET["uri"]
        else:
            uri = "%s://%s%s" % (request.scheme, request.host, request.path)
        aliases = [x.strip() for x in config.get("ontosrv.aliases", "").split(",")]
        base = config.get("ontosrv.base")
        if aliases and base:
            for alias in aliases:
                if not alias: continue
                if uri.startswith(alias):
                    uri = base + uri[len(alias):]
                    break
        # very kludgy
        if uri.endswith(".rdf") or uri.endswith(".n3") \
                or uri.endswith(".html") or uri.endswith(".nt") \
                or uri.endswith(".ttl"):
            uri, self._extension = uri.rsplit(".", 1)
        return URIRef(uri)

    def _label_graph(self):
        labels = list(c.graph.objects(c.graph.identifier, RDFS["label"]))
        label_langs = dict([(x.language, x) for x in labels])
        if None in label_langs:
            no_lang = label_langs[None]
            del label_langs[None]
        elif "en" in label_langs:
            no_lang = label_langs["en"]
        elif labels:
            no_lang = labels[0]
        else:
            no_lang = c.graph.identifier

        lang = request.accept_language.best_match(label_langs.keys())
        if lang:
            c.label = label_langs[lang]
        else:
            c.label = no_lang
        return c.label
    
    @classmethod
    def _fresnel(cls):
        if "lens" in request.GET:
            fresnel_uri = request.GET["lens"]
        else:
            lenses = list(c.graph.objects(c.graph.identifier, ORDF["lens"]))
            if lenses:
                fresnel_uri = lenses[0]
            else:
                fresnel_uri = config.get("ontosrv.default_lens", "http://ordf.org/lens/rdfs")
        tmp = cls.handler.get(fresnel_uri)
        return Fresnel(store=tmp.store, identifier=tmp.identifier)

    def _render_graph(self):
        fresnel = self._fresnel()
        self._label_graph()
        c.stylesheets, content = fresnel.format(c.graph)
        fresnel.rollback()
        c.content = literal(ET.tostring(content, encoding="utf-8").decode("utf-8"))
        return self.render("graph.html")

    def _get_graph(self):
        uri = self._uri()
        response.headers["Vary"] = "Accept"
        content_type, format = self._accept(uri)
        graph = self.handler.get(uri)
        if len(graph) == 0:
            abort(404, "No such graph: %s" % c.graph.identifier)
        if format == "html":
            c.graph = graph
            data = self._render_graph()
        else:
            data = graph.serialize(format=format)
            response.content_type = str(content_type)
        return data

    def _put_graph(self):
        content_type, format = self._content_type()
        uri = self._uri()
        user = c.author
        reason = request.GET.get("reason", "change via web")
        new = Graph(identifier=URIRef(uri))
        new.parse(StringIO(request.body), format=format)
        ctx = self.handler.context(user, reason)
        ctx.add(new)
        ctx.commit()
        log.info("change to %s from %s (%s)" % (uri, user, reason))
        return new.version()

    def index(self):
        if request.method == "GET":
            return self._get_graph()
        elif request.method == "PUT":
            if not config.get("ontosrv.readwrite", False):
                abort(401, "Permission Denied")
            return self._put_graph()
        elif request.method == "HEAD":
            uri = self._uri()
            response.headers["Vary"] = "Accept"
            content_type, format = self._accept(uri)
            graph = self.handler.get(uri)
            if len(graph) == 0:
                abort(404, "No such graph: %s" % c.graph.identifier)
            return ""
        abort(406, "Not Acceptable Here")
