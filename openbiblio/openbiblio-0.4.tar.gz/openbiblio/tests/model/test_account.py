from ordf.term import URIRef

from openbiblio.tests import delete_all
from openbiblio import handler
import openbiblio.model as model

class TestAccount:
    openid = 'http://myopen.id'
    ident = URIRef(openid)
    name = 'Mr Jones and me'
    email = 'xyz@openbiblio.net'

    @classmethod
    def setup_class(self):
        account = model.Account.create(self.openid, self.name, self.email)
        self.account_id = account.identifier
        self.apikey = account.apikey
        current_user = 'ouruser'
        account.save(current_user, 'xyz')

    @classmethod
    def teardown_class(self):
        delete_all()

    def test_01_get_null(self):
        out = model.Account.get_by_openid(self.openid + 'madeup')
        assert out == None, out

    def test_02_get_by_uri(self):
        acc = model.Account.get_by_uri(self.account_id)
        assert acc.identifier == self.account_id, acc.identifier
        out = [x for x in acc.owners][0]
        for (s,p,o) in out.graph.triples((None,None,None)):
            print s,p,o
        # print [(s,p,o) for (s,p,o) in out.graph.triples((None,None,None))]
        assert out.name[0] == self.name, out.name
        assert str(out.openid[0]) == self.openid, out.openid[0]

    def test_02_get_by_openid(self):
        acc = model.Account.get_by_openid(self.openid)
        #assert acc.identifier == self.account_id, [acc.identifier, self.account_id ]
        out = [x for x in acc.owners][0]
        for (s,p,o) in out.graph.triples((None,None,None)):
            print s,p,o
        # print [(s,p,o) for (s,p,o) in out.graph.triples((None,None,None))]
        assert out.name[0] == self.name, out.name
        assert str(out.openid[0]) == self.openid, out.openid[0]


    def test_03_find(self):
        out = [ item.to_dict() for item in model.Account.find()]
        assert len(out) > 0, len(out)
        assert self.account_id in str(out), out

    def test_04_get_by_apikey(self):
        acc = model.Account.get_by_apikey(self.apikey)
        assert acc.identifier == self.account_id, acc.identifier
        assert acc.apikey == self.apikey

    def test_05_owner(self):
        acc = model.Account.get_by_uri(self.account_id)
        out = acc.owners[0]
        assert out.name[0] == self.name, out.name
        assert str(out.openid[0]) == self.openid, out.openid[0]
        assert str(out.mbox[0]) == "mailto:%s" % self.email, out.mbox[0]

    def test_06_get_gravatar_without_mail(self):
        acc = model.Account.get_by_uri(self.account_id)
        bob_avatar = 'http://www.gravatar.com/avatar/18b8b9ef4f299fc8f32cf7ab3a6d4801?s=60&d=identicon'
        assert str(acc.get_avatar) == bob_avatar, acc.get_avatar
 
    def test_07_get_gravatar_with_mail(self):
        acc = model.Account.get_by_uri(self.account_id)
        print acc.to_dict()
        del acc.avatar
        print acc.to_dict()
        person = acc.owners.pop()
        person.mbox = 'bob@example.com'
        person.save(acc)
        print person.to_dict()
        bob_avatar = 'http://www.gravatar.com/avatar/4b9bb80620f03eb3719e0a061c14283d?s=60&d=identicon'
        assert str(acc.get_avatar) == bob_avatar, acc.get_avatar
 
