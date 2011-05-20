# redirect standard search to custom search

site_url = context.portal_url.getPortalObject().absolute_url()
qs = context.REQUEST.QUERY_STRING
context.REQUEST.RESPONSE.redirect('%s/custom_search?%s' % (site_url, qs))
