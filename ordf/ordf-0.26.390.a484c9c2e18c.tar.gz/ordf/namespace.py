"""
Namespace Declarations
======================

In addition to the following RDF namespace declarations, this module
conveniently works around some refactoring that `RDFLib`_ has experienced
to make importing the :class:`~rdflib.namespace.Namespace` class more
uniform.

.. autofunction:: bind_ns
.. autofunction:: register_ns

.. data:: namespaces

A dictionary containing all of the namespaces defined here. The keys are the
names of the namespaces and the values are the namespaces themselves.

.. data:: BIBO
.. data:: BIO
.. data:: CS
.. data:: DBPPROP
.. data:: DCES
.. data:: DC
.. data:: DCAM
.. data:: DOAP
.. data:: FOAF
.. data:: FRBR
.. data:: FRESNEL
.. data:: GND
.. data:: GR
.. data:: LIST
.. data:: LOG
.. data:: OPMV
.. data:: ORDF
.. data:: ORE
.. data:: OWL
.. data:: RDAGR2
.. data:: RDARELGR2
.. data:: RELATIONSHIP
.. data:: SCOVO
.. data:: SKOS
.. data:: TRIG
.. data:: VOID
.. data:: WOT
.. data:: UUID

.. _RDFLib: http://www.rdflib.net/
"""

try:
    from rdflib.namespace import Namespace, RDF, RDFS, XSD
except ImportError:
    from rdflib import Namespace
    RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    RDFS = Namespace('http://www.w3.org/2000/01/rdf-schema#')
    XSD = Namespace('http://www.w3.org/2001/XMLSchema#')

BIBO = Namespace("http://purl.org/ontology/bibo/")
BIO = Namespace("http://purl.org/vocab/bio/0.1/")
CS = Namespace("http://purl.org/vocab/changeset/schema#")
DBPPROP = Namespace("http://dbpedia.org/property/")
DCES = Namespace("http://purl.org/dc/elements/1.1/")
DC = Namespace("http://purl.org/dc/terms/")
DCAM = Namespace("http://purl.org/dc/dcam/")
DOAP = Namespace("http://usefulinc.com/ns/doap#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
FRBR = Namespace("http://purl.org/vocab/frbr/core#")
FRESNEL = Namespace("http://www.w3.org/2004/09/fresnel#")
GND = Namespace("http://d-nb.info/gnd/")
GR = Namespace("http://bibliographica.org/schema/graph#")
ICAL = Namespace("http://www.w3.org/2002/12/cal/ical#")
LIST = Namespace("http://www.w3.org/2000/10/swap/list#")
LOG = Namespace("http://www.w3.org/2000/10/swap/log#")
OPMV = Namespace("http://purl.org/net/opmv/ns#")
ORDF = Namespace("http://purl.org/NET/ordf/")
ORE = Namespace("http://www.openarchives.org/ore/terms/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDAGR2 = Namespace("http://RDVocab.info/ElementsGr2/")
RDARELGR2 = Namespace("http://metadataregistry.org/uri/schema/RDARelationshipsGR2/")
RDFG = Namespace("http://www.w3.org/2004/03/trix/rdfg-1/")
RELATIONSHIP = Namespace("http://purl.org/vocab/relationship/")
REV = Namespace("http://purl.org/stuff/rev#")
SCOVO = Namespace("http://purl.org/NET/scovo#")
SIOC = Namespace("http://rdfs.org/sioc/ns#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
TIME = Namespace("http://www.w3.org/2006/time#")
VOID = Namespace("http://rdfs.org/ns/void#")
WOT = Namespace("http://xmlns.com/wot/0.1/")

UUID = Namespace("urn:uuid:")

namespaces = {
    "rdf": RDF,
    "rdfs": RDFS,
    "bibo": BIBO,
    "bio": BIO,
    "cs": CS,
    "dbpprop": DBPPROP,
    "dces": DCES,
    "dc": DC,
    "dcam": DCAM,
    "doap": DOAP,
    "foaf": FOAF,
    "frbr": FRBR,
    "fresnel": FRESNEL,
    "gnd": GND,
    "gr": GR,
    "ical": ICAL,
    "list": LIST,
    "log": LOG,
    "opmv": OPMV,
    "ordf": ORDF,
    "ore": ORE,
    "owl": OWL,
    "rdaGr2": RDAGR2,
    "rdaRelGr2": RDARELGR2,
    "rdfg": RDFG,
    "relationship": RELATIONSHIP,
    "rev": REV,
    "scovo": SCOVO,
    "sioc": SIOC,
    "skos": SKOS,
    "time": TIME,
    "uuid": UUID,
    "void": VOID,
    "wot": WOT,
    "xsd": XSD
}

def bind_ns(g, namespaces=namespaces):
    """
    Given an :class:`~rdflib.graph.Graph`, bind the namespaces present in
    the dictionary in this module to it for more readable serialisations.

    :param g: an instance of :class:`rdflib.graph.Graph`.
    """
    try:
        [g.bind(*x) for x in namespaces.items()]
    except: ### XXX sometimes gives errors with rdflib sleepycat !?
        pass

def register_ns(prefix, ns):
    """
    Register a namespace for use by ORDF

    :param prefix: the namespace prefix that should be used
    :param namespace: an instance of ordf.namespace.Namespace
    """
    from ordf import namespace
    from logging import getLogger
    log = getLogger("ordf.namespace")
    ns = Namespace(str(ns))
    if hasattr(namespace, prefix.upper()):
        log.warning("Registering %s: <%s> prefix already exists" % (prefix, ns))
    log.debug("Registering %s: <%s>" % (prefix, ns))
    setattr(namespace, prefix.upper().replace("-", "_"), ns)
    namespaces[prefix] = ns

def _init_ns():
    import pkg_resources
    for entrypoint in pkg_resources.iter_entry_points(group="ordf.namespace"):
        init_ns = entrypoint.load()
        init_ns()

    register_ns("sdmx", Namespace("http://purl.org/linked-data/sdmx#"))
    register_ns("sdmxconcept", Namespace("http://purl.org/linked-data/sdmx/2009/concept#"))
    register_ns("sdmxdim", Namespace("http://purl.org/linked-data/sdmx/2009/dimension#"))
    register_ns("sdmxattr", Namespace("http://purl.org/linked-data/sdmx/2009/attribute#"))
    register_ns("sdmxmeasure", Namespace("http://purl.org/linked-data/sdmx/2009/measure#"))
    register_ns("sdmxcode", Namespace("http://purl.org/linked-data/sdmx/2009/code#"))
    register_ns("sdmxsubject", Namespace("http://purl.org/linked-data/sdmx/2009/subject#"))

    register_ns("wdrs", Namespace("http://www.w3.org/2007/05/powder-s#"))
