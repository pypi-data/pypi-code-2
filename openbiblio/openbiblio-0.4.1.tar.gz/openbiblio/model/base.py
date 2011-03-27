import collections
import inspect
import uuid
import re
import types

from ordf.namespace import register_ns, Namespace
register_ns("biblio-ont", Namespace("http://bibliographica.org/onto#"))

import ordf.namespace
from ordf.namespace import FOAF, RDF, RDFS, BIBO, DC, ORDF, OWL
from ordf.term import URIRef, BNode, Literal
from ordf.vocab.owl import Class, AnnotatibleTerms, predicate, object_predicate
from ordf.graph import Graph, ConjunctiveGraph

from openbiblio import handler
from openbiblio.lib.utils import coerce_uri as u, coerce_literal as l, flockdb, private_property

class __mapper__(object):
    """
    Singleton class (should not define the instance at model scope
    like this!) that holds mappings from DomainObject implementations
    and RDF type URIs.
    """
    __registry_c2r__ = {}
    __registry_r2c__ = {}
    def __call__(self, identifier, cls):
        """
        Register an identifier as belonging to the class
        """
        key = inspect.getmodule(cls).__name__ + "." + cls.__name__
        self.__registry_c2r__[key] = identifier
        self.__registry_r2c__[identifier] = cls
    def tordf(self, cls):
        """
        Given a python class or instance, return the RDF type or KeyError
        """
        if not inspect.isclass(cls):
            cls = cls.__class__
        key = inspect.getmodule(cls).__name__ + "." + cls.__name__
        return self.__registry_c2r__[key]
    def topython(self, ident):
        """
        Given a URI return the implementation or KeyError
        """
        return self.__registry_r2c__[ident]
    def implementations(self, graph, ident):
        """
        Given a graph and an identifier contained therin, return
        a list of possible implementations
        """
        implementations = []
        for rdftype in graph.distinct_objects(ident, RDF["type"]):
            try:
                implementations.append(mapper.topython(rdftype))
            except KeyError:
                continue
        return implementations
mapper = __mapper__()

class DomainObject(Class):
    def __init__(self, *av, **kw):
        kwa = kw.copy()
        kwa["skipClassMembership"] = True
        super(DomainObject, self).__init__(*av, **kwa)
        if not kw.get("skipClassMembership"):
            rdfclass = mapper.tordf(self)
            if rdfclass is not None:
                self.type = rdfclass
        self._load_private()
        
    @classmethod
    def instance_namespace(cls):
        """
        Namespace for identifiers. The default constructs a namespace from
        a configured base and the class name in lowercase. If other than the
        default behaviour is desired, override in inheriting classes.
        """
        from pylons import config
        base = config.get("ontosrv.base", "http://localhost:5000/")
        slug = cls.__name__.lower()
        return Namespace(base + slug + "/")

    @classmethod
    def atomic_integer(cls):
        from pylons import config
        serials = config.get("openbiblio.serials", "openbiblio.serials")
        prefix = config.get("openbiblio.serial_prefix", "BB")
        key = str(cls.instance_namespace())
        
    @classmethod
    def new_identifier(cls):
        '''Creates new identifiers in this domain objects namespace using'''
        from pylons import config
        serials = config.get("openbiblio.serials", "openbiblio.serials")
        prefix = config.get("openbiblio.serial_prefix", "BB")
        ns = cls.instance_namespace()
        with flockdb(serials, "w") as db:
            key = str(ns)
            try:
                current = db[key]
            except KeyError:
                current = 9999
            serial = current + 1
            db[key] = serial
        return ns["%s%09d" % (prefix, serial)]

    @classmethod
    def create(cls, uri=None):
        '''Create an object with uri `uri` and associated to a graph identified
        by same uri'''
        if uri is None:
            uri = cls.new_identifier()
        uri = u(uri)
        graph = Graph(identifier=uri)
        out = cls(uri, graph=graph)
        return out

    @classmethod
    def get_by_uri(cls, uri):
        uri = u(uri)
        graph = handler.get(uri)
        if len(graph) == 0:
            raise KeyError("No such graph", uri)
        obj = cls(uri, graph=graph)
        return obj

    @classmethod
    def purge(self, uri):
        uri = u(uri)
        handler.remove(Graph(identifier=uri))
    
    def save(self, user, message=''):
        if not isinstance(self.graph.identifier, URIRef):
            raise TypeError(self.graph.identifier, type(self.graph.identifier), "graph identifier must be URIRef")
        ctx = handler.context(user, message)
        for g in ConjunctiveGraph(self.graph.store).contexts():
            ctx.add(g)
        ctx.commit()
        self._save_private()
    
    def __str__(self):
        return self.graph.serialize(format='n3')

    @classmethod
    def find(cls, limit=20, offset=0):
        rdfcls = mapper.tordf(cls)
        q = '''
        SELECT DISTINCT ?id
        WHERE {
            ?id a %(class_)s
        } OFFSET %(offset)s LIMIT %(limit)s
        ''' % dict(
            class_= rdfcls.n3(),
            limit=limit,
            offset=offset)
        # have to do this first otherwise get closed cursor error
        results = [ u(res[0]) for res in handler.query(q) ]
        results = [ cls.get_by_uri(uri) for uri in results ]
        return results

    def to_dict(self):
        """
        Convenience method: return a dictionary representation of the current object
        """
        cls = self.__class__
        result = {}
        if isinstance(self.identifier, URIRef):
            result["id"] = self.identifier.n3()
        else: ## bnode
            for same in self.sameAs:
                if isinstance(same, URIRef):
                    result["id"] = same.n3()
                    break
        seen = []
        for attrname in [a for a in dir(cls) if not a.startswith("_")]:
            ## special case
            if attrname == 'cached_types':
                continue
            attr = getattr(cls, attrname)
            if isinstance(attr, predicate):
                seen.append(attr.term)
                value = getattr(self, attrname)
                ## special sameAs processing
                if attr.term == OWL["sameAs"] and "id" in result:
                    newvalue = []
                    for v in value:
                        if hasattr(v, "identifier"): node = v.identifier
                        else: node = v
                        if result["id"] != node.n3():
                            newvalue.append(v)
                    value = newvalue
                value = self._convert_to_dict_value(value)
                if value is not None:
                    result[attrname] = value
        for s,p,o in self.graph.triples((self.identifier, None, None)):
            if p in seen:
                continue
            key = self._convert_predicate_to_dict_key(p)
            vlist = result.setdefault(key, [])
            value = self._convert_to_dict_value(o)
            if value is not None:
                vlist.append(value)
        return result

    def _convert_predicate_to_dict_key(self, predicate):
        ns, pfx, local = self.graph.compute_qname(predicate)
        __autons_re = re.compile("^(_[0-9]+|ns[0-9]+)$") ## maybe put htis somewhere else
        if __autons_re.match(ns): ## automatically generated namespaces, unstable prefixes
            key = p.n3()
        else:
            key = "%s:%s" % (ns, local)
        return key
    
    def _convert_to_dict_value(self, value):
        if isinstance(value, collections.Iterable) and not isinstance(value, basestring):
            value = [self._convert_to_dict_value(x) for x in value]
            if len(value) == 1:
                return value[0]
            elif len(value) > 0:
                return value
            return None
        if isinstance(value, Literal):
            if value.datatype is None:
                return unicode(value)
            value = value.toPython()
            if isinstance(value, Literal):
                ### XXX LOSSY WE LOSE DATATYPES HERE WHEN THERE
                ### IS NO PYTHON DATATYPE. WE REALLY NEED TO FIND
                ### A WAY TO ENCODE THIS IN THE JSON
                return unicode(value)
        elif isinstance(value, URIRef):
            return value.n3()
        elif isinstance(value, DomainObject):
            return value.to_dict()
        elif isinstance(value, BNode): ## blank node
            result = {}
            for p in self.graph.distinct_predicates(value):
                key = self._convert_predicate_to_dict_key(p)
                o = list(self.graph.distinct_objects(value, p))
                v = self._convert_to_dict_value(o)
                if v is not None:
                    result[key] = v
        elif value is None:
            return None
        else:
            raise TypeError("Cannot deal with", type(value), value)
        
    def _resolve_predicate(self, key):
        if ":" not in key: ## explicit predicate/property
            if not hasattr(self.__class__, key): ## not there
                raise ValueError("no such predicate", key)
            predicate = getattr(self.__class__, key)
            if not hasattr(predicate, "term"): ## not an explicit predicate
                raise ValueError("no such predicate", key)
            predicate = predicate.term
        elif key.startswith("<") and key.endswith(">"):
            predicate = URIRef(key)
        else: ## key is of form ns:local
            ## could optimise here
            namespaces = dict(self.graph.namespace_manager.namespaces())
            pfx, local = key.split(":", 1)
            ns = namespaces.get(pfx)
            if ns is None:
                raise ValueError("unknown namespace", key)
            predicate = URIRef(ns + local)
        return predicate
    
    def _convert_from_dict_value(self, subject, predicate, value):
        if isinstance(value, basestring):
            if value.startswith('<') and value.endswith('>'):
                obj = URIRef(value[1:-1])
            else:
                obj = Literal(value)
            yield subject, predicate, obj
        elif isinstance(value, dict):
            ### this implementation is wrong actually... what it needs to do is
            ###
            ### 1. check the type on the predicate and look up the correct
            ###     implementation in the mapper
            ### 2. if found, use its from_dict_update or create methods
            ### 3. if not found continue as here
            ###
            ### otherwise, the resolving of explicit predicates, on the implementation
            ### is wrong -- it will use ones from *this* object instead of the embedded
            ### one.
            if "id" in value: ## embeded explicit object
                s = URIRef(value["id"][1:-1])
            else:
                s = BNode()
            yield subject, predicate, s
            for k in value:
                if k in ("id", "type"): ## repeated in from_dict_update... not the best DRY practice...
                    continue
                p = self._resolve_predicate(k)
                # do not process ordf:changeSet!!!
                if p == ORDF["changeset"]:
                    continue
                for statement in self._convert_from_dict_value(s, p, value[k]):
                    yield statement
        else:
            yield subject, predicate, Literal(value)

    def from_dict_update(self, objectdict, append=False):
        '''Update current object with a dictionary of values.'''
        g = Graph()
        for key, value in objectdict.items():
            # delete 'type' from the dict as we do not want to set that
            if key in ("id", "type"):
                continue
            predicate = self._resolve_predicate(key)
            # do not process ordf:changeSet!!!
            if predicate == ORDF["changeset"]:
                continue
            if not isinstance(value, list):
                value = [value]
            for v in value:
                for statement in self._convert_from_dict_value(self.identifier, predicate, v):
                    g.add(statement)
        
        ## now this is a bit tricky because we need to make sure that we
        ## add statements to the right graph and handle blank nodes.
        subjects = [s for s in g.distinct_subjects() if isinstance(s, URIRef)]
        for subject in subjects:
            sgraph = Graph(self.graph.store, identifier=subject)
            if len(sgraph) == 0: ## try to get from the handler...
                sgraph += handler.get(subject)
            if not append:
                ## cannot do a straight delete here in case of blank nodes
                for predicate in sgraph.distinct_predicates(subject):
                    x = sgraph.bnc((subject, predicate, None))
                    sgraph -= x
            ## now populate the graph
            sgraph += g.bnc((subject, None, None))

    @classmethod
    def from_dict(cls, dict_):

        if not 'id' in dict_: # new
            coll = cls.create()
        else: # update (already exists)
            if dict_['id'].startswith('<htt'):
                dict_['id'] = dict_['id'][1:-1]
            coll = cls.get_by_uri(dict_['id'])
           # TODO: check it does not exist
        coll.from_dict_update(dict_)
        return coll

    @property
    def local_path(self):
        if isinstance(self.identifier, BNode):
            for same in self.sameAs:
                return same
        else:
            return self.identifier

    def _load_private(self):
        from pylons import config
        if not hasattr(self, "private_store"):
            return
        dbfile = config.get(self.private_store, self.private_store)
        with flockdb(dbfile) as db:
            try:
                info = db[str(self.identifier)]
                for attr, value in info.items():
                    setattr(self, attr, value)
            except KeyError:
                pass
            
    def _save_private(self):
        from pylons import config
        if not hasattr(self, "private_store"):
            return
        dbfile = config.get(self.private_store, self.private_store)
        info = {}
        for attr in dir(self.__class__):
            if not isinstance(getattr(self.__class__, attr), private_property):
                continue
            if hasattr(self, attr):
                value = getattr(self, attr)
                if isinstance(value, types.GeneratorType):
                    value = list(value)
                info[attr] = value

        with flockdb(dbfile, "w") as db:
            db[str(self.identifier)] = info

