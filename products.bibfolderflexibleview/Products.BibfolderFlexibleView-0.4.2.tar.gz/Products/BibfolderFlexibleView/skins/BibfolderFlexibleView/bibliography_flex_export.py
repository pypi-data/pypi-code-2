## Script (Python) "bibliography_flex_export"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=format='BibTex', output_encoding=None, eol_style=False
##title=
##
request = context.REQUEST
RESPONSE =  request.RESPONSE

if not format: return None


# variante über SESSION-objekt
# eigentlich eleganter, ermöglicht filter-sensitiven export über den grünen pfeil
# in den site-actions, aber probleme mit cache und vor allem, wenn requests nicht
# immer vom selben server beantwortet werden sondern mehrere sich die arbeit teilen

#query = request.SESSION.get('query')


if request.has_key('query'): query = request['query']
else: query = None

if query:
    response_filename = context.getId() + str(hash(str(query))) + '.' + format
    results = context.bibflexview_get_references(query)
    results = [r.getObject() for r in results]
else:
    results = context
    response_filename = context.getId() + '.' + format
    
RESPONSE.setHeader('Content-Type', 'application/octet-stream')
RESPONSE.appendHeader('Cache-Control', 'no-cache')
RESPONSE.setHeader('Content-Disposition',
                   'attachment; filename=%s' %\
                   response_filename)


bibtool = context.portal_bibliography
return bibtool.render(results, format=format, output_encoding=output_encoding, msdos_eol_style=eol_style)
