from pylons import request, response, session, tmpl_context as c
from ordf.pylons.serialiser import search_format
from ordf.pylons import ControllerFactory
from ordf.graph import Graph
from cStringIO import StringIO
import pkg_resources
try:
    import json
except ImportError:
    import simplejson as json

class _XapianController:
    def index(self):
        if not hasattr(self, "search"):
            for entrypoint in pkg_resources.iter_entry_points(group="ordf.xapian"):
                if entrypoint.name == "search":
                    self.search = entrypoint.load()
                    break
        if not hasattr(self, "search"):
            raise ImportError("no plugin in [ordf.xapian] named %s" % self.name)

        c.query = request.GET.get("q", None)
        if c.query:
            c.offset = int(request.GET.get("offset", 0)) if not hasattr(c, 'offset') else c.offset
            c.limit = int(request.GET.get("limit", 20)) if not hasattr(c, 'limit') else c.limit
            c.results = self.search(self.handler.xapian.open(), c.query, c.offset, c.limit)

        mime_type, format = search_format(request)

        if format == "json":
            resp = []
            for row in c.results:
                g = Graph()
                g.parse(StringIO(row.document.get_data()), format="n3")
                r = {
                    "metadata": {
                        "rank": row.rank,
                        "percent": row.percent,
                        "weight": row.weight,
                    },
                    "uri": row.document.get_value(0),
                    "document": g.serialize(format="nt"),
                }
                resp.append(r)
            resp = json.dumps(resp)
        else:
            resp = self._render()
        if c.query:
            self.handler.xapian.close()
        return resp

    def _render(self):
        return self.render("search.html")

def XapianControllerFactory(base, handler):
    return ControllerFactory("XapianController", _XapianController, base, handler)

