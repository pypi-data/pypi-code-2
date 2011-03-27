from ordf.term import URIRef

from openbiblio.tests import delete_all
from openbiblio import handler
from openbiblio.tests import *
import openbiblio.model as model
from ordf.namespace import BIBO

class TestCollection(TestController):
    entrytitle = 'my-test-entry'
    title = 'my-test-collection'
    subject = 'literature'
    openid = 'http://myopen.id/2'

    @classmethod
    def setup_class(self):
        account = model.Account.create(self.openid)
        account.save(account,'new test account for %s' % self.openid)
        self.account_id = account.identifier
        entry = model.Entry.create()
        entry.title = self.entrytitle
        entry.save(account,message='saved new entry')

        collection = model.Collection.create()
        collection.title = self.title
        collection.subject = self.subject
        collection.entries = [ entry ]
        collection.owner = self.account_id
        collection.save(account,message='saved new collection')

        self.collection_id = collection.identifier
        self.entry_id = entry.identifier

        handler.put(account.graph)
        handler.put(collection.graph)
        handler.put(entry.graph)

    @classmethod
    def teardown_class(self):
        delete_all()

    def test_01_get(self):
        collection = model.Collection.get_by_uri(self.collection_id)
        assert collection.title[0] == self.title, collection.title
        account = list(collection.owner)[0]
        assert account.identifier == self.account_id, account
        entries = list(collection.entries)
        assert len(entries) == 1, entries

    def test_02_by_user_openid(self):
        collections = model.Collection.get_by_user_openid(self.openid)
        collectionvalues = [ coll.to_dict().values() for coll in collections ]
        assert self.title[0] in str(collectionvalues), collectionvalues

    def test_03_find(self):
        out = model.Collection.find()
        dicts = []
        for collection in out:
            dicts.append(collection.to_dict())
        assert len(out) > 0, out
        assert self.collection_id in str(dicts), dicts

    def test_04_to_dict(self):
        collection = model.Collection.get_by_uri(self.collection_id)
        out = collection.to_dict()
        assert out['title'] == self.title
        assert out['id'] == self.collection_id.n3()
        assert out['owner']["id"] == self.account_id.n3()

    def test_05_from_dict_create(self):
        onedict = {
            'title': 'Interplanetary flight : an introduction to astronautics',
            "dc:subject" : { "rdf:value": "space" },
            "entries": [
                { "id": self.entry_id.n3(), "title": "new title" }
                ]
        }
        collection = model.Collection.from_dict(onedict)
        id_ = collection.identifier 
        collection.save('xyz', '')
        out = model.Collection.get_by_uri(id_)
        assert out.title[0] == onedict['title'],out.title[0]

        ## test the entry as well...
        entry = model.Entry.get_by_uri(self.entry_id)
        assert entry.title[0] == "new title"
        
    def test_06_from_dict(self):
        newdict = {
            'title': 'Interplanetary flight : an introduction to astronautics',
            'id': self.collection_id
        }
        coll = model.Collection.from_dict(newdict)
        coll.save('xyz', '')
        out = model.Collection.get_by_uri(self.collection_id)
        assert BIBO.Collection in out.type
        assert out.title[0] == newdict['title']

    def test_07_from_dict_update(self):
        account = model.Account.get_by_uri(self.account_id)
        newdict = {
            'title': 'introduction to astronautics',
            'subject': 'astronautics',
        }
        coll = model.Collection.from_dict(newdict)
        coll.owner = [ account ] 
        coll.save("xyz", "")

        newdict = {
            "title": "hello foo bar"
            }
        coll.from_dict_update(newdict)
        coll.save("xyz", "")
        assert "hello foo bar" in coll.title
