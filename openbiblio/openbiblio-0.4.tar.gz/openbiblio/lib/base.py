"""The base Controller API

Provides the BaseController class for subclassing.
"""
from pylons.controllers import WSGIController
from pylons.templating import render_genshi as render
from pylons import tmpl_context as c, request, config, response, session
from pylons.controllers.util import abort

import openbiblio
from openbiblio.lib.helpers import to_int
from openbiblio.model import Account
from ordf.onto.lib.base import BaseController as OBaseController
import pkg_resources

class BaseController(OBaseController):
    """
    Ground rules, really apply to any controller for manipulating DomainObject:

      * an object has an identifier, a URI
      * where there are specialised HTML renderings, they should be used with
        an Accept header of text/html and will not override other content-type
        handlers
      * where there are specialised HTML renderings they will also accept a URL
        for the object ending in .html
      * where there are specialised HTML renderings and the request does not
        end in .html the app will set a Content-Location header that refers to the
        full canonical URL for the object with .html appended
      * mutatis mutandis for JSON renderings
      * all objects will also be retrievable with an RDF Accept header or relevant
         file extensions. normally nothing special has to be done to support this
         save making sure not to override the Graph controller in the routes
      * In all cases a response will contain a Vary: Accept header
      * ALWAYS use c.request_uri and do not try to guess the URI that was
        requested
        
    """

    def __before__(self, action, **params):
        c.site_title = config.setdefault('site_title', 'Non-Bibliographica')
        # Why doesn't setting strict_c to False avoid this ...?
        for attr, val in {'url':'', 'bindings':[], 'boolean':False, 
                          'warnings': None, 'person_total': 0, 
                          'manif_total': 0, 'work_total': 0, 'results': [],
                          'read_user': '', 'graph':None}.items():
            if not hasattr(c, attr): setattr(c, attr, val)

        super(BaseController, self).__before__(action, **params)

        if "uri" in request.GET:
            c.request_uri = request.GET["uri"]
        else:
            c.request_uri = "%s://%s%s" % (request.scheme, request.host, request.path)

        # WARNING: you must use request.GET as request.params appears to alter
        # request.body (it gets url-encoded) upon call to request.params
        c.q = c.query = request.GET.get("q", None)
        c.reqpage = to_int(request.params.get('page', 1),maxn=50)
        c.limit = to_int(request.GET.get('limit', '500'), maxn=5000)
        c.items_per_page = to_int(request.GET.get('items_per_page', 20))
        c.offset = (c.reqpage-1) * c.items_per_page
        c.deliverance_enabled = bool(config.get('deliverance.enabled', ''))
        c.account, c.user, c.author = self._identify()

    # TODO: (?) work out how to use repoze.who.identity stuff
    # identity = request.environ.get('repoze.who.identity') 
    def _identify(self):
        '''This method identifies a user from REMOTE_ADDR or API key.

        @return: (Account, username, username or IP)
        '''
        username = None
        account = None
        author = None

        # see if it was proxied first
        remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', '')
        if not remote_addr:
            remote_addr = request.environ.get('REMOTE_ADDR', 'Unknown IP Address')

        openid = request.environ.get('REMOTE_USER', None)
        if openid is not None:
            identity = request.environ.get("repoze.who.identity")
            if identity is None: ## should only happen in tests!?!?
                identity = { "repoze.who.plugins.openid.username": openid }
            try:
                account = Account.get_by_openid(openid)
            except KeyError:
                username = identity.get('repoze.who.plugins.openid.username')
                if not username or not len(username.strip()) \
                    or not Account.VALID_USERNAME.match(username):
                    username = openid
                # we do not enforce uniqueness of username ...
                account = Account.create(
                    openid=openid,
                    name=identity.get('repoze.who.plugins.openid.fullname'),
                    mbox=identity.get('repoze.who.plugins.openid.email')
                )
                account.save(username, 'New account: %s' % openid)
        else:
            api_key = request.headers.get('x-openbiblio-api-key', '')
            if api_key:
                try:
                    account = Account.get_by_apikey(api_key)
                except KeyError:
                    pass

        if account is not None:
            username = account.pretty_name

        # finally set 'author' string (for use in e.g. changesets)
        if username is not None:
            author = username
        else:
            author = remote_addr
        author = unicode(author)

        return (account, username, author)

