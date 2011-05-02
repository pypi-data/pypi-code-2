## Script (Python) "get_references"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=query
##title=
##

bfvtool = context.portal_bibliography_flexible_view;


# in case we get passed a string as 'query', make sure it gets parsed
query = bfvtool.query_from_string(query)

res = context.portal_catalog.search(query);
#res = context.queryCatalog(query);

return res
