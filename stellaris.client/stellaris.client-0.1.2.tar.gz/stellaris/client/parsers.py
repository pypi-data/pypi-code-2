# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import simplejson, sys

from urlparse import urljoin
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import iterparse, tostring as et_tostring

DATATYPE_MAP = {
'http://www.w3.org/2001/XMLSchema#integer': (None, 'int')
}

class Row(object):
    def __init__(self):
        self._data = {}

    def __setitem__(self, name, value):
        data, lang, datatype = value
        
        try:
            python_module, python_type = DATATYPE_MAP[datatype]
            
            if python_module:
                __import__(python_module)
                cast = getattr(python_module, python_type)
            else:
                cast = getattr(__builtins__, python_type)
                
            data = cast(value)
        except Exception, e:
            # when casting doesnt work
            pass
        
        self._data[name] = data

    def __getitem__(self, name):
        return self._data[name]

    def get(self, k, d=None):
        return self._data.get(k, d)
        
class SPARQLResults(object):
    def __init__(self):
        self.variables = []
        self.rows = []

    def _parse_xml_variable(self, elem):
        # variables are taken care of in head
        pass
        
    def _parse_xml_head(self, elem):
#        print 'head: ', elem
            
        for variable in elem:
#            print 'variable: ', variable.attrib['name']
            self.variables.append(variable.attrib['name'])

    def _parse_xml_sparql(self, elem):
        elem.clear()

    def _parse_xml_results(self, elem):
        pass
#        print "results: ", elem

    def _parse_xml_result(self, elem):
        row = Row()

        for binding in elem:
            value = binding[0]
            
            datatype = value.attrib.get('datatype', None)
            lang = value.attrib.get('xml:lang', None)

            row[binding.attrib['name']] = (value.text, lang, datatype)
        
        self.rows.append(row)
            
    def _parse_xml_binding(self, elem):
        # taken care of in result
        pass
        #print "binding", elem.attrib['name'], elem

    def _parse_xml_literal(self, elem):
        pass
        
    def _parse_xml_uri(self, elem):
        pass
#        print "uri: ", elem.text, elem

    def _parse_xml_bnode(self, elem):
        pass
#        print "bnode: ", elem.text, elem

    def _parse_xml_default(self, elem):
        sys.stderr.write("[ERROR] tag %s, not handled by SPARQL result parser." % elem.tag)
                        
    def parse_xml(self, results):
        context = iterparse(results, events=["end"])

        SPARQL_NS = "http://www.w3.org/2005/sparql-results#"

        def qname(tag):
            return "{%s}%s" % (SPARQL_NS, tag)
        
        def remove_ns(tag):
            return tag[tag.find('}')+1:]
        
        # turn it into an iterator
        context = iter(context)

        # get the root element
        event, root = context.next()

        for event, elem in context:
            f = getattr(self, '_parse_xml_%s' % remove_ns(elem.tag.lower()), self._parse_xml_default)
            f(elem)

    def parse_json(self, results):
        json_res = simplejson.load(results)    
        self.variables = json_res['head']['vars']

        def test_var(v, name):
            try:
                val = res[v][name]
                if val.lower() == "none":
                    return None
                return val
            except KeyError, e:
                return None
        
        for res in json_res['results']['bindings']:
            row = Row()
            for v in res.keys():
                lang = test_var(v, 'xml:lang')
                datatype = test_var(v, 'datatype')
                    
                row[v] = (res[v]['value'], lang, datatype)
            
            self.rows.append(row)

    def __str__(self):
        variables = '\t'.join([v for v in self.variables])        
        rows = '\n'.join(['\t'.join([row.get(v, '') for v in self.variables]) for row in self.rows])

        return "%s\n%s" % (variables, rows)
        
    def __repr__(self):
        return '<SPARQLResults with %s variables and %s rows>' % (len(self.variables), len(self.rows))
            
if __name__ == '__main__':
    from cStringIO import StringIO

    results = """<?xml version="1.0" encoding="utf-8"?>
    <?xml-stylesheet type="text/xsl" href="/static/sparql-xml-to-html.xsl"?>
    <ns0:sparql xmlns:ns0="http://www.w3.org/2005/sparql-results#">
    <ns0:head>
        <ns0:variable name="lang" />
        <ns0:variable name="date" />
        <ns0:variable name="test" />        
    </ns0:head>
    <ns0:results>
        <ns0:result>
            <ns0:binding name="date">
                <ns0:literal>August 16, 1999</ns0:literal>
            </ns0:binding>
            <ns0:binding name="lang">
                <ns0:literal>en</ns0:literal>
            </ns0:binding>
        </ns0:result>
        <ns0:result>
            <ns0:binding name="date">
                <ns0:literal>August 19, 1968</ns0:literal>
            </ns0:binding>
            <ns0:binding name="lang">
                <ns0:literal>de</ns0:literal>
            </ns0:binding>
        </ns0:result>
        <ns0:result>
            <ns0:binding name="date">
                <ns0:literal>not a date</ns0:literal>
            </ns0:binding>
            <ns0:binding name="test">
                <ns0:literal>value</ns0:literal>
            </ns0:binding>
        </ns0:result>                
    </ns0:results>
    </ns0:sparql>"""

    sparql = SPARQLResults()
    sparql.parse_xml(StringIO(results))

    print sparql
