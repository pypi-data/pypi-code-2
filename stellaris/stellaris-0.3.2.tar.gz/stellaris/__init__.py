__VERSION__ = '0.3.1'
__DATE__= '2008/08/22'

try:
    from rdflib import Namespace

    STELLARIS = Namespace("http://www.gac-grid.org/schema/stellaris#")
    RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
except ImportError, e:
    STELLARIS = "http://www.gac-grid.org/schema/stellaris#"
    RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    XSD = "http://www.w3.org/2001/XMLSchema#"
    
