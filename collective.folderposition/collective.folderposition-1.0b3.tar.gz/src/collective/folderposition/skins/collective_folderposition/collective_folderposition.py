## Controller Python Script "collective_folderposition"
##title=Move objects in a ordered folder
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=collective_folderposition, paths, delta=1, selected_obj_paths=None, sort_on="getObjPositionInParent", pagenumber="1", show_all="False", orig_template="@@folder_contents"
##

from Products.CMFPlone import PloneMessageFactory as _
from ZTUtils import make_query

position=collective_folderposition.lower()

ids = [path.rsplit('/', 1)[1] for path in paths]

if selected_obj_paths is None:
    subset_ids = None
else:
    subset_ids = [path.rsplit('/', 1)[1] for path in selected_obj_paths]

if   position=='up':
    context.moveObjectsByDelta(ids, -delta, subset_ids)
elif position=='down':
    context.moveObjectsByDelta(ids, delta, subset_ids)
elif position=='top':
    context.moveObjectsByDelta(ids, -2**32, subset_ids)
elif position=='bottom':
    context.moveObjectsByDelta(ids, 2**32, subset_ids)

context.plone_utils.reindexOnReorder(context)

msg=_(u'Item\'s position has changed.')
context.plone_utils.addPortalMessage(msg)

query = make_query(sort_on=sort_on, pagenumber=pagenumber, show_all=show_all)
url = '%s/%s?%s' % (context.absolute_url(), orig_template, query)
context.REQUEST.RESPONSE.redirect(url)
