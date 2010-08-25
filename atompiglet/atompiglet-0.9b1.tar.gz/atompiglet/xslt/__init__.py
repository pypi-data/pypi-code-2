import os.path
from lxml import etree

atom_to_rdf = etree.XSLT(etree.parse(os.path.join(__path__[0], 'atom_to_rdf.xsl')))

atom_to_legacy_rdf = etree.XSLT(etree.parse(os.path.join(
    __path__[0], 'atom_to_legacy_rdf.xsl')))
