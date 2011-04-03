"""
This module brings OpenCyc piecemeal into ORDF/RDFLib applications.

.. autoclass:: Concept
   :show-inheritance:
.. autofunction:: rdf_data
.. _OpenCyc: http://sw.opencyc.org/
"""

from ordf.graph import ConjunctiveGraph, Graph
from ordf.namespace import register_ns, Namespace, RDF, RDFS, OWL
from ordf.term import BNode, Literal
from urllib import urlencode
from urllib2 import urlopen, HTTPError

CYC = Namespace("http://sw.opencyc.org/concept/")
CYC_ANNOT = Namespace("http://sw.cyc.com/CycAnnotations_v1#")
register_ns("cyc", CYC)
register_ns("cycAnnot", CYC_ANNOT)

from logging import getLogger
log = getLogger(__name__)

def rdf_data():
    """
    Data fixture for OpenCyc. Starts with the top level predicate
    and recurses through all 'owl:DatatypeProperty', 'owl:ObjectProperty',
    predicates and classes present in the returned RDF either as
    subjects or appearing in 'rdfs:domain' or 'rdfs:range'. In this
    way builds up a basic ontology that can be used for reasoning.

    This function may take some time to complete as at the time of
    writing it will yield some 520 distinct graphs.
    """
    g = Graph(identifier=CYC_ANNOT[""])
    g.parse(CYC_ANNOT[""])
    yield g

    seen = set()
    def _f(ident):
        if ident.startswith(CYC[""]) and ident not in seen:
            seen.add(ident)
            x = Graph(identifier=ident)
            log.info("fetching %s" % ident)
            try:
                _g = Graph().parse(ident)
            except HTTPError, e:
                log.error("error fetching %s: %s" % (ident, e))
                return
            x += _g.bnc((ident, None, None))
            yield x
            for s in _g.distinct_subjects(RDF["type"], RDF["Property"]):
                for x in _f(s): yield x
            for s in _g.distinct_subjects(RDF["type"], OWL["AnnotationProperty"]):
                for x in _f(s): yield x
            for s in _g.distinct_subjects(RDF["type"], OWL["DatatypeProperty"]):
                for x in _f(s): yield x
            for s in _g.distinct_subjects(RDF["type"], OWL["ObjectProperty"]):
                for x in _f(s): yield x
            for s in _g.distinct_subjects(RDF["type"], OWL["Class"]):
                for x in _f(s): yield x
            for s in _g.distinct_subjects(RDFS["subClassOf"]):
                for x in _f(s): yield x
            for p in _g.distinct_predicates():
                for x in _f(p): yield x
            for o in _g.bnc((None, RDFS["domain"], None)).distinct_objects():
                for x in _f(o): yield x
            for o in _g.bnc((None, RDFS["range"], None)).distinct_objects():
                for x in _f(o): yield x
            for o in _g.bnc((None, RDFS["subClassOf"], None)).distinct_objects():
                for x in _f(o): yield x

    for g in _f(CYC["Mx4rvViA1pwpEbGdrcN5Y29ycA"]): ## top level predicate
        log.info("Seen %d distinct concepts" % len(seen))
        yield g

class Concept(Graph):
    """
    OpenCyc is very big. For most purposes we don't want to have to store
    the entire knowledge base in our local store, but for inferencing 
    purposes we often will want to store some of the relevant concepts.

    OpenCyc handily provides a search interface that gives results in
    XML, and we use this to retrieve a concept if we don't know it's URI
    beforehand.

    Initialisation of :class:`Concept` takes, as with any other :class:`Graph`
    an optional 'store' argument. If the concept in question does not
    exist in the store it will be fetched and added. The data that is
    returned by OpenCyc will typically include some other resources,
    these are filtered out. Only the blank node closure of the requested
    resource is added to the store.

    The :class:`Concept` class has methods for walking the ontology
    tree, documented below. These can be useful for adding relevant
    resources to the store in an automated way, but can be quite slow
    as they can make a potentially large number of HTTP requests.

    >>> lamb, = Concept.search("lamb", max=1)
    >>> print lamb.cycAnnot()
    (JuvenileFn Sheep)
    >>> for parent in lamb.parents():
    ...     print parent.cycAnnot()
    ...
    Sheep
    JuvenileAnimal
    >>>

    .. automethod:: search
    .. automethod:: parents
    .. automethod:: ancestors
    .. automethod:: cycAnnot
    """
    _not_found = set()
    def __init__(self, *av, **kw):
        super(Concept, self).__init__(*av, **kw)
        if self.one((None, None, None)) is None: 
            log.info("fetching %s" % self.identifier)
            try:
                g = Graph().parse(self.identifier)
                self += g.bnc((self.identifier, None, None))
            except HTTPError, e:
                log.error("error fetching %s: %s" % (self.identifier, e))
                self._not_found.add(self.identifier)

    _nss = { "cyc": "http://ws.opencyc.org/xsd/CycConcepts" }
    @classmethod
    def search(self, name, max=1, exact=True, store="IOMemory"):
        """
        The OpenCyc search interface is not documented anywhere obvious, but
        a very small amount of reverse engineering the JavaScript code on the
        website and analysing the XML given in returned is sufficient to
        implement this method.

        :param name: a text string to search on. This might be the name
            in English of the concept that is of interest
        :param max: maximum number of results to return
        :param exact: exact matches only
        :param store: the RDFLib Store to which any results should be
            added, returned graphs are initialised with this store. The
            default is the string '"IOMemory"'
        :return: an iterator over populated :class:`Concept` graphs for
            each of the search results
        """
        from Ft.Xml.Domlette import NonvalidatingReader
        params = {
            "max": max,
            "isExactMatch": "true" if exact else "false",
            "conceptDetails": "typical",
            "str": name
        }
        uri = "http://sw.opencyc.org//webservices/concept/find?" + urlencode(params)
        fp = urlopen(uri)
        result = NonvalidatingReader.parseStream(fp, uri=uri)
        fp.close()

        for concept in result.xpath("/cyc:concepts/cyc:concept", explicitNss=self._nss):
            extid = concept.xpath("string(cyc:externalId)", explicitNss=self._nss)
            ident = CYC[extid]
            yield Concept(store, identifier=ident)

    def cycAnnot(self):
        """
        Return the Cyc annotation or representation in the Cyc language
        of the current resource.
        """
        _s, _p, o = self.one((self.identifier, CYC_ANNOT["label"], None))
        return o

    def parents(self, restrict=False, seen=set()):
        """
        Walk one step up the class hierarchy by following 'rdfs:subClassOf' 
        links.

        :param restrict: boolean indicating whether parents returned should 
            be restricted to the OpenCyc namespace.
        :param seen: set of identifiers that have already been processed and
            are not therefore to be returned, in order to avoid needless 
            recursion
        :return: an iterator yielding :class:`Concept` for each of the parent
            concepts.
        """
        for cls in self.distinct_objects(self.identifier, RDFS["subClassOf"]):
            if cls in seen: continue
            if restrict and not cls.startswith(CYC[""]): continue
            yield Concept(self.store, identifier=cls)

    def ancestors(self, restrict=False, seen=set()):
        """
        Walk to the top of the class hierarchy recursively using :meth:`parents`.
        Parameters are as with that method.
        """
        for parent in self.parents(restrict=restrict, seen=seen):
            if parent.identifier in seen: continue
            seen.add(parent.identifier)
            yield parent
            for ancestor in parent.ancestors(restrict=restrict, seen=seen):
                if ancestor.identifier in seen: continue
                seen.add(ancestor.identifier)
                yield ancestor

if __name__ == '__main__':
    from logging import basicConfig, DEBUG
    basicConfig(level=DEBUG)

    import doctest
    doctest.testmod()

    for g in rdf_data():
        statement = g.one((g.identifier, RDFS["label"], None))
        if statement is not None:
            print statement[0], statement[2]
