## Script (Python) "get_references"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=query
##title=
##

if hasattr(context, 'buildQuery'):
    q = context.buildQuery()
else: q = {}

return context.portal_bibliography_flexible_view.merge_queries(query, q)
