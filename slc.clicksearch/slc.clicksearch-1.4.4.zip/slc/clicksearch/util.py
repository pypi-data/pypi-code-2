import urllib
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

def current_query(request):
    portal = getSite()
    plone_utils = getToolByName(portal, 'plone_utils')
    encoding = plone_utils.getSiteEncoding()
    qs = request.get('QUERY_STRING', '')
    query = {}
    elems = qs.split('&')
    for elem in elems:
        kv = elem.split('=')
        if len(kv)!=2:
            continue
        query[kv[0]] = urllib.unquote(kv[1]).decode(encoding)
    return query
    
def make_qs(query):
    qs = []
    for q in query.items():
        qs.append('='.join(q))
    return '&'.join(qs)
    
def make_link(request, index, elem):
    query = current_query(request)
    query[index] = elem
    try:
        new_qs = make_qs(query)
    except:
        new_qs = ''
    return "clicksearch?%s" % new_qs

