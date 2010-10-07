## Script (Python) "getIPublicatortemInfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object=None
##title=Returns other needed information of the refered item object
item_metadata = {}

if object is not None:
    try:
        item_metadata['Group'] = object.aq_parent.title_or_id()
    except:
        item_metadata['Group'] = ''
else:
    item_metadata['Group'] = ''

return item_metadata

