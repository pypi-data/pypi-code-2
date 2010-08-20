"""
.. autoclass:: Functions
    :show-inheritance:
.. autoclass:: Function
    :show-inheritance:
"""
from ordf.namespace import register_ns, Namespace
register_ns("cofogs", Namespace("http://purl.org/okfn/def/unstats/cofog#"))
register_ns("cofog", Namespace("http://purl.org/okfn/id/unstats/cofog#"))
from ordf.namespace import COFOG, COFOGS, DC, OWL, SKOS, RDF, RDFS, XSD
from ordf.graph import Graph, ConjunctiveGraph
from ordf.term import Literal, URIRef
from ordf.vocab.owl import Property
from ordf.vocab.skos import ConceptScheme, Concept, ConceptInstance
from telescope import Select, v
try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET
import pkg_resources, os

_COFOG_SOURCE = URIRef("http://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=ACT_OTH_DFLT_LAYOUT&StrNom=CL_COFOG99")

class Functions(ConceptScheme):
    """
    A SKOS Concept Scheme representing the COFOG

    >>> functions = Functions()
    >>> functions.load()
    >>> dev = functions.byFog("06.2")
    >>> print [str(name) for name in dev.label]
    ['Community development']
    >>> print [str(notation) for notation in dev.notation]
    ['06.2']
    >>> for broader in dev.broader:
    ...     print [str(name) for name in broader.label]
    ...
    ['Housing and community amenities']
    >>>

    :param graph:
        If not None, place the definition into the given graph, or retrieve
        indivudual concepts from the given graph.

    .. automethod:: load
    .. automethod:: byFog
    """
    def __init__(self, graph=None):
        if graph is None: graph = Graph()
        super(Functions, self).__init__(COFOGS.Functions, graph=graph)
        self._funcCache = {}
        self.graph.add((self.identifier, DC.source, _COFOG_SOURCE))

    def load(self, graph=None):
        """
        Load the functions into the given graph

        :param graph: 
            If *None*, load the functions into *self.graph* instead
        """
        if graph is None: graph = self.graph
            
        cofog_data = os.path.join("data", "cofog")
        for filename in pkg_resources.resource_listdir("unstats", cofog_data):
#        for filename in ["COFOG99_EN.xml"]: # only do the english one for now
            cofog_file = os.path.join(cofog_data, filename)
            contents = pkg_resources.resource_stream("wdmmg.vocab", cofog_file).read()
            tree = ET.fromstring(contents)
            root = tree
            for classification in root.findall("Classification"):
                self.graph.add((self.identifier, DC.identifier, Literal(classification.get("id"))))
                label = classification.find("Label/LabelText")
                text = label.text.strip()
                lang = label.get("language").lower()
                self.label = Literal(text, lang=lang)
                self.prefLabel = Literal(text, lang=lang)
                for item in classification.findall("Item"):
                    code, label = item.findall("Label/LabelText")
                    level = int(item.get("idLevel"))
                    code = code.text.strip()
                    if code == "TOTAL":
                        _code = [code]
                    elif level == 1:
                        _code = [code[2:4]]
                    elif level == 2:
                        _code = [code[2:4], code[4:6]]
                    elif level == 3:
                        _code = [code[2:4], code[4:6], code[6:8]]
                    # strip leading zeros on the parts
                    _code = ".".join(x[1] if x.startswith("0") else x for x in _code)
                    # put back leading zero on first part. who thought of this stuff?
                    if len(_code) == 1 or _code[1] == ".": _code = "0" + _code

                    ident = COFOG[_code]
                    text = label.text.strip()
                    lang = label.get("language").lower()
                    function = self.get(ident, graph=graph)
                    function.type = COFOGS.Function
                    function.label = Literal(text, lang=lang)
                    function.prefLabel = Literal(text, lang=lang)
                    function.notation = Literal(_code, datatype=COFOGS["Code"])
                    function.graph.add((function.identifier, COFOG.level, Literal(level)))
                    function.graph.add((function.identifier, RDFS.isDefinedBy, COFOG[""]))
                    if level == 1:
                        self.addTop(function)
                    else:
                        function.graph.add((function.identifier, SKOS.inScheme, self.identifier))
                        upper, lower = _code.rsplit(".", 1)
                        parent = self.get(COFOG[upper])
                        function.graph.add((function.identifier, SKOS.broader, parent.identifier))
                        parent.graph.add((parent.identifier, SKOS.narrower, function.identifier))

    def byFog(self, code, graph=None):
        """
        Retrieve a function individual by the given code. If *graph*
        is not *None* look there, otherwise look in the store backing
        *self.graph*
        """
        if graph is None:
            graph = ConjunctiveGraph(self.graph.store)
        function = self._funcCache.get(code)
        if function is None:
            q = Select([v.ident], distinct=True).where(
                (v.ident, SKOS.notation, Literal(code, datatype=COFOGS["Code"]))
                )
            for ident in graph.query(q.compile()):
                function = self.get(ident)
                self._funcCache[code] = function
        return function

class Function(Concept):
    """
    The SKOS concept of a Function of Government. This is the OWL class.
    Actual individual functions have this as their type.
    """
    def __init__(self, scheme):
        super(Function, self).__init__(COFOG.Function, graph=scheme.graph)
        self.label = Literal("Function", lang="en")
        self.prefLabel = Literal("Function", lang="en")
        self.graph.add((COFOG.Function, RDFS.isDefinedBy, COFOG[""]))

def rdf_data():
    graph = Graph(identifier=COFOGS[""])

    scheme = Functions(graph=graph)
    Function(scheme)

    level = Property(COFOG.level, graph=graph, baseType=OWL.DatatypeProperty)
    level.domain = COFOG.Function
    level.range = XSD.integer
    level.label = Literal("Function Level", lang="en")
    level.graph.add((COFOG.level, RDFS.isDefinedBy, graph.identifier))

    graph.add((COFOGS["Code"], RDF.type, RDFS.Datatype))
    graph.add((COFOGS["Code"], RDFS.label, Literal("Function Code", lang="en")))
    graph.add((COFOGS["Code"], RDFS.isDefinedBy, graph.identifier))

    concepts = Graph(identifier=COFOG[""])
    scheme.load(concepts)

    yield graph
    yield concepts

if __name__ == '__main__':
    import doctest
    doctest.testmod()
