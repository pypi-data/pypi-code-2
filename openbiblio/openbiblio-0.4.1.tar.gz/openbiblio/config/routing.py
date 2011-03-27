"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

    # for the time being catch everything but soon we will be more specific
    # e.g. restrict to work|person|entity ...
    
from autoneg.accept import negotiate
def negotiator(content_type, format):
    """
    Content type autonegotiation guard for routes. First
    checks the URL to see if it ends in a recognisable
    extension. Then it checks the Content-type header
    for PUT/POST requests, Then it checks the Accept
    header for GET/HEAD requests.
    """
    if format in ("xml", "pretty-xml"): ending = ".rdf" ## silly special cases...
    else: ending = "." + format
    ctype, subtype = content_type.split("/")
    cfg = ((ctype, subtype, [format]),)
    def _neg(env, spec):
        if env["PATH_INFO"].endswith(ending):
            spec["format"] = format
            spec["content_type"] = content_type
            return True
        elif env["REQUEST_METHOD"] in ("GET", "HEAD"):
            accept = env.get("HTTP_ACCEPT")
            if accept == None:
                accept = ""
            for result in negotiate(((ctype, subtype, format),), accept, strict=True):
                spec["format"] = format
                spec["content_type"] = content_type
                return True
        elif env["REQUEST_METHOD"] in ("PUT", "POST"):
            for result in negotiate(((ctype, subtype, format),), env["CONTENT_TYPE"], strict=True):
                spec["format"] = format
                spec["content_type"] = content_type
                return True
        return False
    return _neg

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE

    map.connect('home', '/', controller='home', action='index')
    # proxied items
    map.connect('about', '/about', controller='home', action='about')
    map.connect('get-involved', '/get-involved', controller='home',
            action='get_involved')

    map.connect('proxy', '/proxy', controller='proxy', action='index')
    map.connect('sparql', '/sparql', controller='sparql', action='index')
    map.connect('search', '/search', controller='search', action='index')
    map.connect('graph', '/graph', controller='graph', action='index')
    map.connect('add', '/add', controller='graph', action='add')
    map.connect('import', '/import', controller='remote', action='index')
    map.connect('uuid', '/api/uuidalloc', controller='uuidalloc', action='index')

    map.connect("isbn", "/isbn/{isbn}", controller="isbn", action="index")
    map.connect("isbn", "/isbn", controller="isbn", action="index")

    map.connect("collection", "/collection/search", controller="collection",
            action="search", conditions=dict(method=["GET"], function=negotiator("application/json", "json")))
    map.connect("collection", "/collection/search", controller="collection",
            action="search", conditions=dict(method=["GET"], function=negotiator("text/javascript", "json")))

    map.connect("collection", "/collection", controller="collection",
            action="create", conditions=dict(method=['POST']))
    map.connect("collection", "/collection/{collection}", controller="collection",
            action="update", conditions=dict(method=['POST']))
    
    map.connect("collection", "/collection/{collection}",
                controller="collection", action="get_html",
                conditions=dict(method=["GET"], function=negotiator("text/html", "html")))
    map.connect("collection", "/collection/{collection}", 
            controller="collection", action="get_json",
                conditions=dict(method=["GET"], function=negotiator("application/json", "json")))
    map.connect("collection", "/collection/{collection}", 
            controller="collection", action="get_json",
                conditions=dict(method=["GET"], function=negotiator("text/javascript", "json")))

    map.connect("collection", "/collection", controller="collection", action="index_html",
                conditions=dict(method=["GET"], function=negotiator("text/html", "html")))
    map.connect("collection", "/collection", controller="collection", action="index_json",
                conditions=dict(method=["GET"], function=negotiator("application/json", "json")))
    map.connect("collection", "/collection", controller="collection", action="index_json",
                conditions=dict(method=["GET"], function=negotiator("text/javascript", "json")))

    map.connect("modeview", "/modelview", controller="modelview", action="index")

    # map.connect("changeset", "/changeset/{changeset}", 
    #             controller="changeset", action="view")
    map.connect("changesets", "/changeset", 
                controller="changeset", action="index")

    map.connect('/account', controller='account', action='index')
    map.connect('/account/login', controller='account', action='login')
    map.connect('/account/logout', controller='account', action='logout')
    map.connect('/account/{username}', controller='account', action='view',
                conditions=dict(method=["GET"], function=negotiator("text/html", "html")))


    def make_rdf_rest(rdf_serialisation):
        map.connect('/*path', controller='graph', action='rdf_serialise',
                    conditions=dict(method=["GET", "HEAD"], function=negotiator(*rdf_serialisation)))
        map.connect('/*path', controller='graph', action='rdf_replace',
                    conditions=dict(method=["PUT"], function=negotiator(*rdf_serialisation)))
        map.connect('/*path', controller='graph', action='rdf_append',
                    conditions=dict(method=["POST"], function=negotiator(*rdf_serialisation)))
        map.connect('/*path', controller='graph', action='rdf_delete',
                    conditions=dict(method=["DELETE"], function=negotiator(*rdf_serialisation)))
    make_rdf_rest(("application/rdf+xml", "pretty-xml"))
    make_rdf_rest(("text/n3", "n3"))

    ## these have to be first otherwise text/plain (ntriples) overrides from a web browser
    map.connect('/*path', controller='graph', action='bibtex_view',
                conditions=dict(method=["GET"], function=negotiator("text/x-bibtex", "bibtex")))
    map.connect('/*path', controller='graph', action='json_view',
                conditions=dict(method=["GET"], function=negotiator("text/javascript", "json")))
    
    map.connect('/*path', controller='graph', action='html_view',
                conditions=dict(method=["GET"], function=negotiator("text/html", "html")))
    map.connect('/*path', controller='graph', action='html_view',
                conditions=dict(method=["GET"], function=negotiator("application/xhtml+html", "html")))

    ## put this after so we don't accidentally get text/plain when we didn't explicitly
    ## request it.
    make_rdf_rest(("text/plain", "nt"))

    ## and the catchall
    map.connect('/*path', controller='graph', action='html_view', conditions=dict(method=["GET"]))

    return map
