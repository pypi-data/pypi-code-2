"""Collections API.

Create, view, search and update Collections (i.e. lists of works).

########
######## Design considerations:
########
#
# For the future: wouldn't this discussion be better in a ticket :)
#
###
#
# RP: have you looked at the issues in the tracker (#18, #19)?  The whole point
# is to entirely replace the 'store/model' code here with the model.Collection
# object.
#
###
### - why a new namespace "bb" when bibo:Collection is perfectly
###    adequate and conveys the intended meaning?
###
# ANS: (RP) this was discussed on irc with you and was agreed that this was not
# identical to a bibo:Collection (more about a journal list).  Since we did not
# establish a clear answer we coined our own.
###
### - why use rdfs:member? it's kind of an abstract property. not
###    strictly wrong to use but dcterms:isPartOf is better and clearer.
###
# This is one of the things I think is is a bit problematic in RDF - too many
# schemas with similar predicates/classes :). I asked Ben O'Steen and after
# discussion he suggested just doing with rdfs:member
###
### - PUT vs. POST -> PUT replaces, POST appends
###
# I'd disagree here. In most RESTish things I've done we've ended up needing to
# allow POST and PUT for update (whether replace or append) due to vagaries of
# browsers or code.
###
### - Content-types. A PUT/POST request should look at the
###    content-type header and accept json if json is specified
###    it should accept some RDF variant if RDF is specified.
###    Not doing this *removes* or *replaces* functionality
###    instead of adding it. Remember that there is also a get
###    parameter to override the header for the HTTP-challenged.
###
#     RP: content autoneg is great but it also adds complexities for clients. I
#     also think it is probably a good idea to separate API functionality from
#     the WUI (for example going forward the load and behaviour on the two
#     areas may be very different. Hence in ticket 19 I explicitly suggest
#     moving the API to /api/collection or similar.
########
######## Implementation details
########
#
# The answer to most of this is a) this was first time working with the system
# (and I was in a hurry) b) this is supposed to all be replaced by use of
# model.Collection (see ticket #19).
#
###
### - there should never, or almost never, be a reason to do
###    "<%s>" % foo_uri, use foo_uri.n3() instead, that's what it is for.
### - is there a particular reason to be using handler.store.rdflib.cursor()
###    instead of just handler.query()?
###    - this is also very dangerous because using it directly won't resolve
###       any datatypes and can give incorrect or confusing results. worst
###       case see the pattern in controllers/graph.py using sparql_query()
###    - answer: because the cursor needs to get closed so use the above
###       referenced pattern until this is fixed in the handler.
### - why all this creating an N3 file and then parsing it instead of
###    just creating a memory graph and using its API? the only time
###    there is really a reason for that is in quick in-place test fixtures
### - the JSON serialisation / deserialisation code needs to take into
###    account datatypes. this doesn't matter much for collections but
###    will for people and books. otherwise dates, for example, won't
###    be indexed and sortable properly.
###
"""
import logging
import uuid
try:
    import json
except ImportError:
    import simplejson as json

from pylons import request, url, wsgiapp
from pylons.decorators import jsonify

from openbiblio.lib.base import BaseController, render, request, c, abort, response
from openbiblio.model.account import Account
from openbiblio.model.collection import Collection
from openbiblio.model.entry import Entry
from openbiblio import handler
log = logging.getLogger(__name__)

from ordf.term import URIRef

class CollectionController(BaseController):

    def index_html(self):
        c.collection_list = Collection.find()
        for collection in c.collection_list:
            for account in collection.owner:
                owner = Account.get_by_uri(account.to_dict()['id'][1:-1])
                account.avatar = owner.avatar
                account.accountName = owner.accountName
        response.headers["Vary"] = "Accept"
        return render('collection_list.html')

    @jsonify
    def index_json(self):
        response.headers["Vary"] = "Accept"
        return {
            'doc': __doc__,
            'doc_url': None
            }
        
    def get_html(self, collection):
        if c.request_uri.endswith(".html"):
            c.request_uri = c.request_uri[:-5]
        try:
            c.model = Collection.get_by_uri(c.request_uri)
        except KeyError:
            abort(404)
        c.booklist = []
        for book in c.model.entries:
            c.booklist.append(Entry.get_by_uri(book.identifier))
        c.owners = []
        for owner in c.model.owner:
            c.owners.append(Account.get_by_uri(owner.identifier))
        ## for some reaosn this doesn't take if done before the render...
        response.headers["Vary"] = "Accept"
        response.headers["Content-Location"] = c.model.identifier + ".html"
        return render("collection.html")
    
    @jsonify
    def get_json(self, collection):
        if c.request_uri.endswith(".json"):
            c.request_uri = c.request_uri[:-5]
        try:
            collectionobj = Collection.get_by_uri(c.request_uri)
        except KeyError:
            abort(404)
        response.headers["Vary"] = "Accept"
        response.headers["Content-Location"] = collectionobj.identifier + ".json"
        return collectionobj.to_dict()
    
    def _request_json(self):
        return request.params

    @jsonify
    def create(self):
        if not c.user:
            # leave as 200 as 401 gets caught and redirected to login
            # (pointless for an api)
            # response.status_code = 401
            return {'status': 401, 'error': 'Not authorised - no user provided'}

        if c.account is None:
            return {'status': 404, 'error': 'Not authorised - no acount found'}

        try:
            data = self._request_json()
            collection = Collection.from_dict(data)
            collection.owner = c.account.identifier
            collection.save(c.author, "Creating collection: %s" % collection.identifier)
            #account.save(account.graph.n3(), "adding: %s" % collection.identifier)
            return {'status': 200, 
                    'uri': collection.identifier, 
                    'title':collection.title[0],
                    'local_path': collection.local_path}
        except Exception, inst:
            #response.status_code = 500
            return {'status': 500, 'error': 'Error: %s' % inst}

    @jsonify
    def update(self, collection):
        if c.account is None:
            return abort(403)
        try:
            import urllib
            ## this is because pylons is being very stupid
            unquoted = request.body.replace("+", " ").rstrip("=")
            unquoted = urllib.unquote(unquoted)
            newdata = json.loads(unquoted)
        except:
            log.debug("update collection: bad data: %s" % unquoted)
            abort(400)
            
        log.debug("update collection: %s" % newdata)
        if "id" not in newdata:
            abort(400)
        try:
            ident = newdata["id"].lstrip("<").rstrip(">")
            collection = Collection.get_by_uri(ident)
        except KeyError:
            abort(404)

        try:
            collection.from_dict_update(newdata)
            logging.info('updated collection: \n%s' % collection.to_dict())
            collection.save(c.author, "Updated collection: %s" % collection.identifier)
            return {'status': 'ok'}
        except Exception:
            from traceback import format_exc
            log.error(format_exc())
            abort(400)

    @jsonify
    def search(self):
        user = request.params.get('user', '')
        if user == '' :
            abort(400) ## need a user
        return {
            'status': 'ok',
            'rows': [c.to_dict() for c in Collection.get_by_user_uri(URIRef(user))],
            }
