# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist, ZIB, AstroGrid-D
# This software is licensed under the software license specified at
# http://www.gac-grid.org/

# this is a work-around of the SPARQL XML-serialization in rdflib which does
# not work on all installation due to a bug in the python sax-parser
# We rely on ElementTree which is only available in Python 2.5

from cStringIO import StringIO

try:
    from xml.etree.cElementTree import Element, SubElement, ElementTree, ProcessingInstruction
    import xml.etree.cElementTree as ET
except ImportError:
    from cElementTree import Element, SubElement, ElementTree
    import cElementTree as ET

from rdflib import URIRef, BNode, Literal, __version__ as rdflib_version

SPARQL_XML_NAMESPACE = u'http://www.w3.org/2005/sparql-results#'
XML_NAMESPACE = "http://www.w3.org/2001/XMLSchema#"

name = lambda elem: u'{%s}%s' % (SPARQL_XML_NAMESPACE, elem)
xml_name = lambda elem: u'{%s}%s' % (XML_NAMESPACE, elem)

def variables(results):
    # don't include any variables which are not part of the
    # result set
    #res_vars = set(results.selectionF).intersection(set(results.allVariables))
    selF = results.selectionF
    
    # this means select *, use all variables from the result-set
    if len(selF) == 0:
        res_vars = results.allVariables
    else:
        res_vars = [v for v in selF] # if v in results.allVariables]
    
    # from rdflib 2.4.1, the ? is removed from vars
    (v1, v2, v3) = rdflib_version.split('.')
    if  int(v1) >= 2 and int(v2) >= 4 and int(v3) >= 1:
        return res_vars
    else:
        return [v[1:] for v in res_vars]
    
def header(results, root):
    head = SubElement(root, name(u'head'))
    
    # the header contains all the variables even if there is no results
    # for the variable
    (v1, v2, v3) = rdflib_version.split('.')
    if (int(v1) >= 2 and int(v2) >= 4 and int(v3) >= 1):
        res_vars = results.selectionF
    else:        
        res_vars = [v[1:] for v in results.selectionF]
    
    for var in res_vars:
        v = SubElement(head, name(u'variable'))
        # remove the ?
        v.attrib[u'name'] = var

        
def binding(val, var, elem):    
    if val == None:
        return
        
    bindingElem = SubElement(elem, name(u'binding'))
    bindingElem.attrib[u'name'] = var

    if isinstance(val,URIRef):
        varElem = SubElement(bindingElem, name(u'uri'))
    elif isinstance(val,BNode) :
        varElem = SubElement(bindingElem, name(u'bnode'))
    elif isinstance(val,Literal):
        varElem = SubElement(bindingElem, name(u'literal'))
        
        if val.language != "" and val.language != None:
            varElem.attrib[xml_name(u'lang')] = str(val.language)
        elif val.datatype != "" and val.datatype != None:
            varElem.attrib[name(u'datatype')] = str(val.datatype)

    #print val, unicode(val)
    varElem.text = unicode(val)

def res_iter(results):
    res_vars = variables(results)
    
    for row in results.selected:
        if len(res_vars) == 1:
            row = (row, )
        
        yield zip(row, res_vars)
              
def result_list(results, root):
    resultsElem = SubElement(root, name(u'results'))
    
    #ordered = results.orderBy
    
    #if ordered == None:
    #    ordered = False
    
    # removed according to the new working draft (2007-06-14)    
    # resultsElem.attrib[u'ordered'] = str(ordered)
    # resultsElem.attrib[u'distinct'] = str(results.distinct)

    for row in res_iter(results):
        resultElem = SubElement(resultsElem, name(u'result'))
        # remove the ? from the variable name
        for (val, var) in row:
            binding(val, var, resultElem)
    
def serializeXML(results):    
    root = Element(name(u'sparql'))
    
    header(results, root)
    result_list(results, root)
    
    out = StringIO()
    tree = ElementTree(root)

    # xml declaration must be written by hand
    # http://www.nabble.com/Writing-XML-files-with-ElementTree-t3433325.html
    out.write('<?xml version="1.0" encoding="utf-8"?>')
    out.write('<?xml-stylesheet type="text/xsl" href="/static/sparql-xml-to-html.xsl"?>')
    tree.write(out, encoding='utf-8')
    
    return out.getvalue()
