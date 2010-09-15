## Script (Python) "subsiteAdvancedQueryCatalog"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=REQUEST=None,show_all=0,quote_logic=0,quote_logic_indexes=['SearchableText','Description','Title'],use_types_blacklist=False,show_inactive=False,use_navigation_root=False,subsite_paths=False,parent_only=False
##title=wraps the portal_catalog with a rules qualified query
##
from ZODB.POSException import ConflictError
from Products.ZCTextIndex.ParseTree import ParseError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot

from Products.AdvancedQuery import AdvancedQuery, In, Not

results=[]
catalog=context.portal_catalog
indexes=catalog.indexes()
query={}
show_query=show_all
second_pass = {}

if REQUEST is None:
    REQUEST = context.REQUEST

def quotestring(s):
    return '"%s"' % s
    

def quotequery(s):
    if not s:
        return s
    try:
        terms = s.split()
    except ConflictError:
        raise
    except:
        return s
    tokens = ('OR', 'AND', 'NOT')
    s_tokens = ('OR', 'AND')
    check = (0, -1)
    for idx in check:
        if terms[idx].upper() in tokens:
            terms[idx] = quotestring(terms[idx])
    for idx in range(1, len(terms)):
        if (terms[idx].upper() in s_tokens and
            terms[idx-1].upper() in tokens):
            terms[idx] = quotestring(terms[idx])
    return ' '.join(terms)

# We need to quote parentheses when searching text indices (we use
# quote_logic_indexes as the list of text indices)
def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s

def ensureFriendlyTypes(query):
    ploneUtils = getToolByName(context, 'plone_utils')
    portal_type = query.get('portal_type', [])
    if not same_type(portal_type, []):
        portal_type = [portal_type]
    Type = query.get('Type', [])
    if not same_type(Type, []):
        Type = [Type]
    typesList = portal_type + Type
    if not typesList:
        friendlyTypes = ploneUtils.getUserFriendlyTypes(typesList)
        query['portal_type'] = friendlyTypes

def rootAtNavigationRoot(query):
    if 'path' not in query:
        query['path'] = getNavigationRoot(context)

def listifySubsitePaths(exclude_paths):
    paths = filter(lambda c: c not in '"[', exclude_paths)
    paths = filter(lambda c: c not in "']", paths)
    if list(paths.split(','))[0] == '' and len(list(paths.split(','))) == 1:
        return list()
    return list(paths.split(', '))
    
# Avoid creating a session implicitly.
for k in REQUEST.keys():
    if k in ('SESSION',):
        continue
    v = REQUEST.get(k)
    if v and k in indexes:
        if k in quote_logic_indexes:
            v = quote_bad_chars(v)
            if quote_logic:
                v = quotequery(v)
        query[k] = v
        show_query = 1
    elif k.endswith('_usage'):
        key = k[:-6]
        param, value = v.split(':')
        second_pass[key] = {param:value}
    elif k in ('sort_on', 'sort_order', 'sort_limit'):
        if k == 'sort_limit' and not same_type(v, 0):
            query[k] = int(v)
        else:
            query[k] = v

for k, v in second_pass.items():
    qs = query.get(k)
    if qs is None:
        continue
    query[k] = q = {'query':qs}
    q.update(v)


# doesn't normal call catalog unless some field has been queried
# against. if you want to call the catalog _regardless_ of whether
# any items were found, then you can pass show_all=1.
if show_query:
    try:
        if use_types_blacklist:
            ensureFriendlyTypes(query)
        if use_navigation_root:
            rootAtNavigationRoot(query)
        query['show_inactive'] = show_inactive
        adv_query = catalog.makeAdvancedQuery(query)
        ignore_paths = listifySubsitePaths(subsite_paths)
        if parent_only == "true" and len(ignore_paths) > 0:
            adv_query = adv_query & ~ In('path', ignore_paths, filter=True)
        results = catalog.evalAdvancedQuery(adv_query)
    except ParseError:
        pass

return results
