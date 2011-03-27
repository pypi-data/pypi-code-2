import shelve
from traceback import format_exc
from hashlib import sha1
from .base import *

from openbiblio.lib.utils import private_property

log = __import__("logging").getLogger(__name__)

class Account(DomainObject):
    '''User accounts based on openids.
    
    OpenID url is used as identifier for the graph and object.
    '''
    accountServiceHomepage = predicate(FOAF.accountServiceHomepage)
    accountName = predicate(FOAF.accountName)
    avatar = predicate(FOAF.img)

    apikey = private_property("apikey")
    private_store = "openbiblio.account_private"
    apikey_store = "openbiblio.apikeys"
    
    def save(self, *av, **kw):
        from pylons import config
        ## save apikey -> identifier mapping
        apikeydb = config.get(self.apikey_store, self.apikey_store)
        with flockdb(apikeydb, "w") as db:
            db[str(self.apikey)] = self.identifier
        super(Account, self).save(*av, **kw)
        for owner in self.owners:
            owner._save_private()
            
    @classmethod
    def get_by_apikey(cls, apikey):
        from pylons import config
        apikeydb = config.get(cls.apikey_store, cls.apikey_store)
        with flockdb(apikeydb) as db:
            uri = db[str(apikey)]
        return cls.get_by_uri(uri)
   
    @classmethod
    def get_by_openid(cls, openid):
        openid = u(openid)
        q = u"""
        SELECT DISTINCT ?account WHERE {
            ?person foaf:openid %s .
            ?person foaf:account ?account .
        }
        """ % openid.n3()
        for account, in handler.query(q):
            return cls.get_by_uri(account)
        raise KeyError(openid)
    
    @classmethod
    def get_by_name(cls, name):
        name = l(name)
        q = u"""
        SELECT DISTINCT ?account WHERE {
            ?account foaf:accountName %s
        }
        """ % name.n3()
        persons = []
        for account, in handler.query(q):
            persons.append(cls.get_by_uri(account))
        return persons

    @classmethod
    def create(cls, openid, name=None, mbox=None):
        from uuid import uuid4
        identifier = cls.new_identifier()
        account_name = str(identifier).split('/')[-1]
        graph = handler.get(identifier)
        account = cls(identifier=identifier, graph=graph)
        account.accountName = l(account_name)
        account.apikey = uuid4()
        if "#" in identifier:
            pident = URIRef(identifier + "-owner")
        else:
            pident = URIRef(identifier + "#owner")
        person = Person(graph=graph, identifier=pident)
        person.openid = u(openid)
        if name is not None:
            person.name = l(name)
        if mbox is not None:
            if not mbox.startswith("mailto:"):
                mbox = "mailto:" + mbox
            person.mbox = [u(mbox)]
            person.mbox_sha1sum = [l(sha1(mbox).hexdigest())]
        person.account = account
        ## actually should do this in save... but a bit tricky...
        person._save_private() 
        account.avatar = account.get_avatar
        return account

    @property
    def pretty_name(self):
        for owner in self.owners:
            for name in owner.name:
                return name
        for name in self.accountName:
            return name
        return self.identifier
    
    @property
    def owners(self):
        owners = []
        for person in self.graph.subjects(FOAF.account, self.identifier):
                owners.append(Person(person, graph=self.graph))
        return owners

    @property
    def collections(self):
        from openbiblio.model import Collection
        collections = Collection.get_by_user_uri(self.identifier)
        return collections

    @property
    def get_avatar(self):
        person = self.owners.pop()
        return person.get_avatar()
                
mapper(FOAF.OnlineAccount, Account)

class Person(DomainObject):
    name = predicate(FOAF.name)
    openid = predicate(FOAF.openid)
    nick = predicate(FOAF.nick)
    mbox_sha1sum = predicate(FOAF.mbox_sha1sum)
    account = object_predicate(FOAF.account, Account)

    mbox = private_property("mbox", default=[]) ## still a list for uniformity with ODM
    private_store = "openbiblio.person_private"

    def get_avatar(self):
        import urllib, hashlib
        default = 'identicon'
        size = 60
        mbox = self.mbox
        if type(mbox) == list:
            if len(mbox) != 0:
                mbox = mbox[0]
        if len(mbox) != 0:
            email = mbox.split(':')[-1]
        else:
            email = self.identifier
        gravatar_url = "http://www.gravatar.com/avatar/" + \
            hashlib.md5(email.lower()).hexdigest() + "?"
        gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
        return URIRef(gravatar_url)

mapper(FOAF.Person, Person)
