## Script (Python) "lingua_folder_cut"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Cut objects from a folder
##
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
message = _(u'Please select one or more items to delete.')

paths = context.REQUEST.get('paths', [])
portal = context.portal_url.getPortalObject()
REQUEST = context.REQUEST

if not paths:
    return context.plone_folder_cut()

cp_list = []
for path in paths:
    obj = portal.restrictedTraverse(path)
    REQUEST.set('paths', ['/'.join(obj.getPhysicalPath())])
    obj.aq_inner.aq_parent.plone_folder_cut()
    cp_list.append(REQUEST['__cp'])

linguaface_tool = getToolByName(context, 'linguaface_tool')
cp = linguaface_tool.assembleCopies( cp_list, 1)
message = _(u'${count} item(s) cut.', mapping={u'count' : len(paths)})
context.plone_utils.addPortalMessage(message)
