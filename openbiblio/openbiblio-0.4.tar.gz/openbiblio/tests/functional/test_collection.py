import uuid
import json
import datetime
from StringIO import StringIO

from ordf.graph import Graph, ConjunctiveGraph
from ordf.term import URIRef, Literal
from openbiblio.model.collection import Collection
from openbiblio.model.account import Account
from openbiblio.tests import *
from openbiblio import handler

## XXX this is hardcoded because the config is not conveniently
## accessible...
http_host = "localhost:5000"
http_base = "http://localhost:5000"

class TestCollectionController(TestController):
    @classmethod
    def teardown_class(cls):
        delete_all()

    def test_index_html(self):
        """get an HTML list of collections with Accept header"""
        oururl = url(controller="collection", action="index_html")
        response = self.app.get(oururl, headers={"Accept": "text/html"})
        assert "Vary" in response.headers, response.headers
        assert response.headers["Vary"] == "Accept", response.headers
        
    def test_index_json(self):
        """get a JSON list of collections with Accept header"""
        oururl = url(controller="collection", action="index_json")
        response = self.app.get(oururl, headers={"Accept": "text/javascript"})
        assert 'doc' in response
        assert 'doc_url' in response
        assert "Vary" in response.headers, response.headers
        assert response.headers["Vary"] == "Accept", response.headers
    
    def test_search(self):
        """search for a collection by user"""
        ouropenid = "http://test.org/me"
        ourusername = "Bit Bucket"
        ouruser = Account.create(ouropenid, name=ourusername)
        ouruser.save(ouropenid)
        c1 = Collection.create()
        c2 = Collection.create()
        c1.owner = ouruser
        c2.owner = ouruser
        c1.save(ouropenid)
        c2.save(ouropenid)
        
        oururl = url(controller='collection', action='search',
                user=ouruser.identifier)
        response = self.app.get(oururl, headers={"Accept": "text/javascript"})

        data = json.loads(response.body)
        assert data['status'] == 'ok'
        assert len(data['rows']) == 2, len(data['rows'])
        firstrow = data['rows'][0]
        firstowner = firstrow["owner"]
        assert firstowner["id"] == ouruser.identifier.n3()

    def test_create(self):
        """create a collection"""
        title = 'my title'
        subject = 'orientalism'
        ourlist = {
            'subject': subject,
            'title': title,
            'entries': []
            }
        ouropenid = 'http://test.org/test-create'
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser,message='new user created')

        oururl = url(controller='collection', action='create')
        response = self.app.post(oururl, params=ourlist,  
                extra_environ=dict(
                    REMOTE_USER=ouropenid,
                ), status=[200,401,302])
        if response.status_int == 302:
            response = response.follow()
            assert 'Login' in response, response

        data = response.json
        assert data is not None
        assert 'uri' in data, data

        collection_uri = data['uri']

        graph = handler.get(collection_uri)
        assert graph, collection_uri

        dctitle = URIRef('http://purl.org/dc/terms/title')
        title_triple = (URIRef(collection_uri),dctitle,Literal(title))
        assert title_triple in graph

    def test_get_html(self):
        """get a collection with an HTML Accept header"""
        title = "Untitled"
        ouropenid = "http://test.org/me-get"
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser)
        c1 = Collection.create()
        c1.title = title
        c1.owner = ouruser
        c1.save("testing", "why not")

        ## you will see this pattern repeated. it is because pylons is
        ## stupid and makes it hard to pass an actual hostname to the
        ## test harness
        oururl = c1.identifier[len(http_base):]
        response = self.app.get(oururl,
                                headers={"Accept": "text/html"},
                                extra_environ={"HTTP_HOST": str(http_host)})

        assert "Vary" in response.headers, response.headers
        assert response.headers["Vary"] == "Accept", response.headers
        assert "Content-Location" in response.headers, response.headers
        assert response.headers["Content-Location"] == c1.identifier + ".html", response.headers

        assert "<h1>Collection:" in response, response

    def test_get_html_ext(self):
        """get a collection with a .html extension"""
        title = "Untitled"
        ouropenid = "http://test.org/me-get"
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser)
        c1 = Collection.create()
        c1.title = title
        c1.owner = ouruser
        c1.save(ouropenid)

        response = self.app.get(c1.identifier + ".html", headers={"Accept": "text/html"})
        assert "<h1>Collection:" in response, response

    def test_get_json(self):
        """get a collection with a JSON Accept header"""
        title = "Untitled"
        ouropenid = "http://test.org/me-get"
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser)
        c1 = Collection.create()
        c1.title = title
        c1.owner = ouruser
        c1.save(ouropenid)

        response = self.app.get(str(c1.identifier), headers={"Accept": "text/javascript"})

        assert "Vary" in response.headers, response.headers
        assert response.headers["Vary"] == "Accept", response.headers
        assert "Content-Location" in response.headers, response.headers
        assert response.headers["Content-Location"] == c1.identifier + ".json", response.headers

        assert '"type": "<http://purl.org/ontology/bibo/Collection>"' in response, response

    def test_get_json_ext(self):
        """request for a collection with .json extension"""
        title = "Untitled"
        ouropenid = "http://test.org/me-get"
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser)
        c1 = Collection.create()
        c1.title = title
        c1.owner = ouruser
        c1.save(ouropenid)

        response = self.app.get(c1.identifier + ".json", headers={"Accept": "text/javascript"})
        assert '"type": "<http://purl.org/ontology/bibo/Collection>"' in response, response

    def test_notfound(self):
        """request for a nonexistent collection"""
        oururl = url(controller="collection", action="get_json", collection="nonexistent")
        self.app.get(oururl, headers={"Accept": "text/javascript"}, status=404)
        
    def test_update(self):
        """update a collection with JSON POST"""
        title = "Untitled"
        ouropenid = "http://test.org/me-update"
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser)
        c1 = Collection.create()
        c1.title = title
        c1.owner = ouruser
        c1.save(ouruser.graph.n3())
        
        colldict = c1.to_dict()
        colldict['title'] = 'my new title'
        response = self.app.post(str(c1.identifier),
                                 params=json.dumps(colldict),
                                 extra_environ={ "REMOTE_USER": ouropenid }
                                 )
        data = response.json
        assert data['status'] == "ok", data

        graph = handler.get(c1.identifier)
        assert graph, c1.identifier

        dctitle = URIRef('http://purl.org/dc/terms/title')
        title_triple = (URIRef(c1.identifier),dctitle,Literal(title))
        assert c1.identifier in graph.serialize(),graph

    def test_get_rdf(self):
        """RDF Response.
        Make sure that when a request is made for an RDF type with an appropriate
        Accept header that we hit the graph controller"""
        
        title = "Untitled"
        ouropenid = "http://test.org/me-get"
        ouruser = Account.create(ouropenid, name="Bit Bucket")
        ouruser.save(ouruser)
        c1 = Collection.create()
        c1.title = title
        c1.owner = ouruser
        c1.save(ouropenid)

        response = self.app.get(str(c1.identifier), headers={"Accept": "text/n3"})

        assert response.status.startswith("303"), response.status
        assert "Location" in response.headers
        location = response.headers["Location"]
        assert location == c1.identifier + ".n3", location
