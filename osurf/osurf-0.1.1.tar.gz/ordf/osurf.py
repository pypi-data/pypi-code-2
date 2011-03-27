try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import base64
import re

from ordf.graph import Graph, _Graph
from ordf.handler import HandlerPlugin
from ordf.term import URIRef, BNode, Literal
from ordf.utils import get_identifier
from surf.store import Store as SurfStore

class Surf(HandlerPlugin):
    def __init__(self, *av, **kw):
        self.endpoint = kw.get("endpoint", "http://localhost:8890/")
        self.store = SurfStore(
            reader="sparql_protocol",
            writer="sparql_protocol",
            endpoint=self.endpoint,
            )
    def __getitem__(self, key):
        ident = get_identifier(key)
        g = Graph(identifier=ident)
        q = "CONSTRUCT { ?s ?p ?o } WHERE { GRAPH %s { ?s ?p ?o } }" % ident.n3()
        result = self.store.execute_sparql(q)
        for row in result["results"]["bindings"]:
            statement = []
            for pos in "spo":
                term = row[pos]
                if term.startswith("_:"):
                    term = virtuoso_nodeid_to_bnode(term[2:])
                statement.append(term)
            g.add(statement)
        return g
    
    def __setitem__(self, key, g):
        assert isinstance(g, _Graph)
        self.store.execute_sparql("CLEAR GRAPH %s" % g.identifier.n3())
        for s,p,o in g:
            if isinstance(s, BNode):
                s = virtuoso_bnode_to_nodeid(s)
            if isinstance(o, BNode):
                o = virtuoso_bnode_to_nodeid(o)
            self.store.add_triple(s,p,o,g.identifier)
        self.store.save()
    
    def __delitem__(self, key):
        ident = get_identifier(key)
        self.store.remove_triple(None, None, None, ident)
        self.store.save()

    def query(self, q):
        from SPARQLWrapper import SPARQLWrapper, JSON
        ## surf doesn't do construct properly
        q = q.strip()
        if "CONSTRUCT {" in q.upper() or q.upper().startswith("DESCRIBE"):
            construct = True
            wrapper = SPARQLWrapper(self.endpoint)
        else:
            construct = False
            wrapper = SPARQLWrapper(self.endpoint, returnFormat=JSON)
        wrapper.setQuery(q)
        results = wrapper.query().convert()
        if not construct:
            var = results["head"]["vars"]
            results = [BoundRow(var, x) for x in results["results"]["bindings"]]
        return results

class BoundRow(object):
    def __init__(self, var, row):
        self.vars = var
        self.row = row
    def __getitem__(self, key):
        if isinstance(key, int):
            key = self.vars[key]
	if key not in self.row:
            return False
        value = self.row[key]
        value = json_to_rdflib(value)
        if isinstance(value, BNode):
            value = virtuoso_nodeid_to_bnode(value)
        return value
    def __iter__(self):
        for v in self.vars:
            yield self[v]
            
####
#### BEGIN HACKS AND MONKEY PATCHES
####
    
## hack to change BNode's random identifier generator to be
## compatible with Virtuoso's needs
from time import time
from random import choice, seed
from string import ascii_letters, digits
seed(time())

__bnode_old_new__ = BNode.__new__

@staticmethod
def __bnode_new__(cls, value=None, *av, **kw):
    if value is None:
        value = choice(ascii_letters) + \
            "".join(choice(ascii_letters+digits) for x in range(7))
    return __bnode_old_new__(cls, value, *av, **kw)
BNode.__new__ = __bnode_new__
## end hack

## hack to transform rdflib's bnodes to virtuoso's and back again
## from http://packages.python.org/virtuoso
def virtuoso_bnode_to_nodeid(bnode):
    from string import ascii_letters
    iri = bnode
    for c in bnode[1:]:
        if c in ascii_letters:
            # from rdflib not virtuoso
            iri = "b" + "".join(str(ord(x)-38) for x in bnode[:8])
            break
    return URIRef("nodeID://%s" % iri)

def virtuoso_nodeid_to_bnode(iri):
    from string import digits
#    iri = iri[9:] # strip off "nodeID://"
    bnode = iri
    if len(iri) == 17:
        # assume we made it...
        ones, tens = iri[1::2], iri[2::2]
        chars = [x+y for x,y in zip(ones, tens)]
        bnode = "".join(str(chr(int(x)+38)) for x in chars)
    return BNode(bnode)

### ripped from surf SVN
def json_to_rdflib(obj):
    """Convert a json result entry to an rdfLib type."""
    try:
        type = obj["type"]
    except KeyError:
        raise ValueError("No type specified")

    if type == 'uri':
        return URIRef(obj["value"])
    elif type == 'literal':
        if "xml:lang" in obj:
            return Literal(obj["value"], lang=obj['xml:lang'])
        else:
            return Literal(obj["value"])
    elif type == 'typed-literal':
        return Literal(obj["value"], datatype=URIRef(obj['datatype']))
    elif type == 'bnode':
        return BNode(obj["value"])
    else:
        return None
