from .base import *
from .entry import Entry
from .account import Account
    
class Collection(DomainObject):
    '''Collections of entries (books, articles etc).
    '''
    title = predicate(DC["title"])
    subject = predicate(DC["subject"])
    # owner = object_predicate(
    entries = object_predicate(DC.hasPart, Entry)
    owner = object_predicate(BIBO.owner, Account)
    created = predicate(DC.created)

    @classmethod
    def get_by_user_openid(cls, openid):
        q = u"""PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        SELECT DISTINCT ?doc
        WHERE { 
          ?doc bibo:owner ?account .
          ?person foaf:openid <%s> .
          ?person foaf:account ?account .
        }
        """ % openid
        readinglist = []
        for collection, in handler.query(q):
            readinglist.append(cls.get_by_uri(collection))
        return readinglist
    @classmethod
    def get_by_user_uri(cls, user):
        if type(user) == str:
            user = URIRef(user)
        q = u"""PREFIX bibo: <http://purl.org/ontology/bibo/>
        PREFIX dc: <http://purl.org/dc/terms/>
        SELECT DISTINCT ?doc 
        WHERE { 
          ?doc bibo:owner %s .
        } 
        """ % user.n3()
        readinglist = []
        for collection in handler.query(q):
            readinglist.append(cls.get_by_uri(str(collection[0])))
        return readinglist

    @classmethod
    def find(cls, limit=20, offset=0):
        rdfcls = mapper.tordf(cls)
        q = '''PREFIX bibo: <http://purl.org/ontology/bibo/>
        SELECT DISTINCT ?id
        WHERE {
            ?id bibo:owner ?owner .
        } OFFSET %(offset)s LIMIT %(limit)s
        ''' % dict(
            class_= rdfcls.n3(),
            limit=limit,
            offset=offset)
        # have to do this first otherwise get closed cursor error
        results = [ u(res[0]) for res in handler.query(q) ]
        results = [ cls.get_by_uri(uri) for uri in results ]
        return results

mapper(BIBO.Collection, Collection)
