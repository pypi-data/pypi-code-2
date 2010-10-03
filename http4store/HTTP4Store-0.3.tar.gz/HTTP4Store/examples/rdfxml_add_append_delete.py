#!/usr/bin/python
# -*- coding: utf-8 -*-

from HTTP4Store import HTTP4Store
from pprint import pprint

# defaults to 'http://localhost:5000'
e = HTTP4Store('http://localhost:8000')
pprint(e.status())

r = e.del_graph("http://example.org/relsext")

relsext="""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="info:fedora/dataset:1">
    <rdf:type rdf:resource="http://vocab.ouls.ox.ac.uk/dataset/scheme#DataSet"></rdf:type>
    <rdfs:label xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">/</rdfs:label>
    <dataset:physicalPath xmlns:dataset="http://vocab.ouls.ox.ac.uk/dataset/scheme#">/</dataset:physicalPath>
    <dcterms:created xmlns:dcterms="http://purl.org/dc/terms/">2006-2-24</dcterms:created>
  </rdf:Description>

</rdf:RDF>
"""

added_triple="""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="info:fedora/dataset:1">
     <dataset:addendum xmlns:dataset="http://vocab.ouls.ox.ac.uk/dataset/scheme#">test</dataset:addendum>
  </rdf:Description>
</rdf:RDF>
"""

q = """PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?s ?p ?o WHERE {
 GRAPH <http://example.org/relsext> {
  ?s ?p ?o}
} LIMIT 10
"""

r = e.add_graph("http://example.org/relsext", relsext, "xml")
assert r.status == 201

print "Query: %s\n\n"
pprint(e.sparql(q))

r =  e.append_graph("http://example.org/relsext", added_triple, "xml")
print r.status

print "===" * 20
print "After adding a triple:"
pprint(e.sparql(q))

print "=*=" * 20
print "Getting the raw response object back:"
resp_obj = e.sparql(q, get_raw_response_obj=True)
print "Status: %s\n\n Content: %s" % (resp_obj.status, pprint(resp_obj.content))
