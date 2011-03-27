from openbiblio.tests import *
from ordf.term import URIRef
import openbiblio.model as model


class TestAccountController(TestController):
    openid = 'https://myopen.id/someperson'
    ident = URIRef(openid)
    name = 'test user'
    email = 'xyz@openbiblio.net'
    current_user = 'testuser'
    
    @classmethod
    def setup_class(self):
        self.account = model.Account.create(self.openid, self.name, self.email)
        self.account.save(self.current_user, 'xyz')

    def test_index(self):
        response = self.app.get(url(controller='account', action='index'))
        assert 'Account' in response, response
        assert response.status_int == 200
        assert 'Login' in response

    def test_index_logged_in(self):
        user_id = self.account.identifier.rsplit("/", 1)[-1]
        response = self.app.get(url(controller='account', action='index'),
            extra_environ={'REMOTE_USER': self.openid})
        assert 'Account' in response, response
        assert response.status_int == 200

    def test_auth_with_api_key(self):
        apikey = str(self.account.apikey)
        userid = self.account.identifier
        allaccounts = len(list(model.Account.find()))
        print apikey
        response = self.app.get(url(controller='account', action='index'),
            headers={'x-openbiblio-api-key': apikey})
        allaccountsnow = len(list(model.Account.find()))
        assert response.status_int == 200
#        assert 'My Account' in response, response ## disabled because of missing template-foo
        assert str(userid.split("/")[-1]) in response
        # check that we are using an existing account, and not created a brand new
        # account:
        assert allaccounts == allaccountsnow, allaccountsnow 

