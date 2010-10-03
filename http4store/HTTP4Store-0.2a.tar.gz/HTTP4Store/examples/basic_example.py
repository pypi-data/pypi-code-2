# for pretty printing:
from pprint import pprint


from HTTP4Store import HTTP4Store

print "Creating a client for a 4Store httpd, running at port 8000"
print "[] $ 4s-httpd -p 8000 {name-of-kb}"
store = HTTP4Store('http://localhost:8000')
print "Getting status:"
status = store.status()
print ">>> status = store.status() # status is a dict"
print "This httpd is accessing a kb called %s, and has the following status: %s/%s [running/outstanding queries]" % (status['kb'], status['running'], status['outstanding'])

print "Attempting to load in the SIOC-project schema, as demo'ed by the PHP client library for 4Store, shown at http://apassant.net/blog/2009/07/27/simple-php-library-4store"
print ">>> response = store.add_from_uri('http://rdfs.org/sioc/ns')"
response = store.add_from_uri('http://rdfs.org/sioc/ns')
print "Asserting that the return status was 201:"
print ">>> assert response.status == 201"
assert response.status == 201
print "Asserted with a msg body of:"
print response.content

print "Running a SPARQL query:"
print """SELECT ?s WHERE 
         { <http://rdfs.org/sioc/ns#Item> ?s ?o }"""
print "Again, copying the usage shown in the PHP library:"
print """>>> sparql_response = store.sparql("select ?s where { <http://rdfs.org/sioc/ns#Item> ?s ?o }")"""
sparql_response = store.sparql("select ?s where { <http://rdfs.org/sioc/ns#Item> ?s ?o }")

print "Printing out the response:"
pprint(sparql_response)

print "Now to delete that graph:"
print """>>> delete_response = store.del_graph('http://rdfs.org/sioc/ns')"""
delete_response = store.del_graph('http://rdfs.org/sioc/ns')
assert delete_response.status == 200
